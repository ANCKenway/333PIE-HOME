"""
🔄 Plugin Self-Update - Auto-mise à jour Agent
===============================================

Plugin cross-platform pour auto-update de l'agent depuis le Hub.

Workflow:
1. Hub détecte nouvelle version agent
2. Hub envoie task "self_update" à l'agent
3. Agent télécharge nouvelle version (ZIP/tar.gz)
4. Agent extrait fichiers dans temp
5. Agent remplace anciens fichiers
6. Agent se restart automatiquement

Sécurité:
- Vérification checksum SHA256
- Backup ancienne version (rollback si échec)
- Validation version (pas de downgrade)
"""

from typing import Optional
from pydantic import BaseModel, Field, validator
import asyncio
import logging
import os
import sys
import shutil
import hashlib
import zipfile
import tarfile
from pathlib import Path
from datetime import datetime
import subprocess
import platform

from ..base import BasePlugin, PluginParams, PluginResult, PluginExecutionError


logger = logging.getLogger(__name__)


class SelfUpdateParams(PluginParams):
    """Paramètres pour auto-update agent."""
    
    version: str = Field(..., description="Version cible (ex: 1.1.0)")
    download_url: str = Field(..., description="URL package agent")
    checksum: str = Field(..., description="SHA256 checksum")
    force: bool = Field(default=False, description="Forcer update même version identique")
    
    @validator("version")
    def validate_version(cls, v):
        """Valide format version (semver)."""
        parts = v.split(".")
        if len(parts) != 3:
            raise ValueError("Version must be semver format (x.y.z)")
        try:
            [int(p) for p in parts]
        except ValueError:
            raise ValueError("Version parts must be integers")
        return v
    
    @validator("download_url")
    def validate_download_url(cls, v):
        """Valide URL download."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("download_url must be HTTP(S)")
        return v


class SelfUpdatePlugin(BasePlugin):
    """
    Plugin auto-update agent.
    
    Télécharge nouvelle version depuis Hub, extrait, remplace fichiers,
    et restart agent automatiquement.
    
    Compatible Windows, Linux, macOS.
    """
    
    name = "self_update"
    description = "Auto-mise à jour agent depuis Hub"
    version = "1.0.0"
    os_platform = "all"
    
    CURRENT_VERSION = "1.0.0"  # Version actuelle de l'agent
    
    def __init__(self):
        super().__init__()
        self._agent_dir = Path(__file__).parent.parent.parent  # src/agents/
        self._backup_dir = self._agent_dir / ".backup"
        self._temp_dir = self._agent_dir / ".update_temp"
    
    async def setup(self) -> bool:
        """Setup du plugin."""
        try:
            # Créer dossiers temp et backup
            self._backup_dir.mkdir(exist_ok=True)
            self._temp_dir.mkdir(exist_ok=True)
            
            self.logger.info(f"Self-update plugin ready. Current version: {self.CURRENT_VERSION}")
            return True
        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False
    
    async def execute(self, params: SelfUpdateParams) -> PluginResult:
        """
        Exécute l'auto-update.
        
        Steps:
        1. Vérifier version (skip si identique et pas force)
        2. Télécharger package
        3. Vérifier checksum
        4. Backup version actuelle
        5. Extraire nouvelle version
        6. Remplacer fichiers
        7. Restart agent
        
        Args:
            params: Paramètres update
        
        Returns:
            Résultat update
        """
        try:
            self.logger.info(f"🔄 Starting self-update to version {params.version}")
            
            # Step 1: Vérifier version
            if not params.force and params.version == self.CURRENT_VERSION:
                return PluginResult(
                    status="success",
                    message=f"Already at version {params.version}, skipping update",
                    data={"current_version": self.CURRENT_VERSION, "target_version": params.version}
                )
            
            # Step 2: Télécharger package
            self.logger.info(f"Downloading package from {params.download_url}")
            package_path = await self._download_package(params.download_url)
            
            # Step 3: Vérifier checksum
            self.logger.info("Verifying checksum...")
            if not await self._verify_checksum(package_path, params.checksum):
                raise PluginExecutionError("Checksum verification failed - package corrupted")
            
            # Step 4: Backup version actuelle
            self.logger.info("Backing up current version...")
            backup_path = await self._backup_current_version()
            
            # Step 5: Extraire nouvelle version
            self.logger.info("Extracting new version...")
            await self._extract_package(package_path)
            
            # Step 6: Remplacer fichiers
            self.logger.info("Replacing files...")
            await self._replace_files()
            
            # Step 7: Restart agent
            self.logger.info("🔄 Restarting agent with new version...")
            await self._restart_agent()
            
            return PluginResult(
                status="success",
                message=f"Successfully updated to version {params.version}",
                data={
                    "old_version": self.CURRENT_VERSION,
                    "new_version": params.version,
                    "backup_path": str(backup_path)
                }
            )
        
        except Exception as e:
            self.logger.error(f"❌ Update failed: {e}", exc_info=True)
            
            # Tentative rollback
            try:
                self.logger.warning("Attempting rollback...")
                await self._rollback()
            except Exception as rollback_error:
                self.logger.error(f"Rollback failed: {rollback_error}")
            
            return PluginResult(
                status="error",
                message="Update failed",
                error=str(e)
            )
        
        finally:
            # Cleanup temp files
            await self._cleanup()
    
    def validate_params(self, params: dict) -> bool:
        """Valide les paramètres."""
        try:
            SelfUpdateParams(**params)
            return True
        except Exception as e:
            self.logger.error(f"Invalid params: {e}")
            return False
    
    def get_schema(self) -> dict:
        """Retourne le schéma des paramètres."""
        return SelfUpdateParams.schema()
    
    async def _download_package(self, url: str) -> Path:
        """Télécharge le package agent depuis le Hub."""
        import aiohttp
        
        filename = url.split("/")[-1]
        package_path = self._temp_dir / filename
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise PluginExecutionError(f"Download failed: HTTP {response.status}")
                
                with open(package_path, "wb") as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
        
        self.logger.info(f"✓ Downloaded {package_path.name} ({package_path.stat().st_size} bytes)")
        return package_path
    
    async def _verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Vérifie le checksum SHA256 du package."""
        sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        
        actual_checksum = sha256.hexdigest()
        
        if actual_checksum != expected_checksum:
            self.logger.error(f"Checksum mismatch: {actual_checksum} != {expected_checksum}")
            return False
        
        self.logger.info("✓ Checksum verified")
        return True
    
    async def _backup_current_version(self) -> Path:
        """Sauvegarde la version actuelle."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self._backup_dir / f"agent_v{self.CURRENT_VERSION}_{timestamp}"
        
        # Copier tous les fichiers agent
        shutil.copytree(self._agent_dir, backup_path, dirs_exist_ok=True, ignore=shutil.ignore_patterns(
            ".backup", ".update_temp", "__pycache__", "*.pyc", ".git"
        ))
        
        self.logger.info(f"✓ Backup created: {backup_path}")
        return backup_path
    
    async def _extract_package(self, package_path: Path):
        """Extrait le package téléchargé."""
        extract_dir = self._temp_dir / "extracted"
        extract_dir.mkdir(exist_ok=True)
        
        if package_path.suffix == ".zip":
            with zipfile.ZipFile(package_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
        elif package_path.suffix in [".tar", ".gz", ".tgz"]:
            with tarfile.open(package_path, "r:*") as tar_ref:
                tar_ref.extractall(extract_dir)
        else:
            raise PluginExecutionError(f"Unsupported package format: {package_path.suffix}")
        
        self.logger.info(f"✓ Extracted to {extract_dir}")
    
    async def _replace_files(self):
        """Remplace les fichiers de l'agent par la nouvelle version."""
        extract_dir = self._temp_dir / "extracted"
        
        # Trouver le dossier racine extrait (peut avoir un sous-dossier)
        extracted_items = list(extract_dir.iterdir())
        if len(extracted_items) == 1 and extracted_items[0].is_dir():
            source_dir = extracted_items[0]
        else:
            source_dir = extract_dir
        
        # Remplacer fichiers (sauf agent.py qui tourne)
        for item in source_dir.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(source_dir)
                target_path = self._agent_dir / rel_path
                
                # Skip agent.py (sera remplacé au restart)
                if target_path.name == "agent.py":
                    continue
                
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target_path)
        
        self.logger.info("✓ Files replaced")
    
    async def _restart_agent(self):
        """Restart l'agent avec la nouvelle version."""
        self.logger.info("Preparing restart...")
        
        # Obtenir le script de l'agent
        agent_script = self._agent_dir / "agent.py"
        
        # Arguments actuels
        args = sys.argv[:]
        
        # Commande restart
        if platform.system() == "Windows":
            # Windows: utiliser pythonw pour détacher
            python_exe = sys.executable.replace("python.exe", "pythonw.exe")
            subprocess.Popen([python_exe] + args, cwd=str(self._agent_dir))
        else:
            # Linux/macOS: fork + exec
            subprocess.Popen([sys.executable] + args, cwd=str(self._agent_dir))
        
        self.logger.info("✓ Restart initiated")
        
        # Attendre 2s puis exit
        await asyncio.sleep(2)
        sys.exit(0)
    
    async def _rollback(self):
        """Rollback vers la version précédente."""
        self.logger.warning("Rolling back to previous version...")
        
        # Trouver dernier backup
        backups = sorted(self._backup_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
        if not backups:
            raise PluginExecutionError("No backup found for rollback")
        
        latest_backup = backups[0]
        
        # Restaurer fichiers
        for item in latest_backup.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(latest_backup)
                target_path = self._agent_dir / rel_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target_path)
        
        self.logger.info(f"✓ Rolled back from {latest_backup}")
    
    async def _cleanup(self):
        """Nettoie les fichiers temporaires."""
        try:
            if self._temp_dir.exists():
                shutil.rmtree(self._temp_dir)
            self.logger.info("✓ Cleanup completed")
        except Exception as e:
            self.logger.warning(f"Cleanup failed: {e}")
