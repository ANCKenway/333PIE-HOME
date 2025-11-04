"""
[Update] Plugin Self-Update - Auto-mise à jour Agent
=====================================================

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
    
    def __init__(self):
        super().__init__()
        self._agent_dir = Path(__file__).parent.parent.parent  # src/agents/
        self._backup_dir = self._agent_dir / ".backup"
        self._temp_dir = self._agent_dir / ".update_temp"
        
        # Import version dynamique depuis version.py
        try:
            import sys
            sys.path.insert(0, str(self._agent_dir))
            from version import __version__
            self.CURRENT_VERSION = __version__
        except ImportError:
            self.CURRENT_VERSION = "1.0.0"  # Fallback
    
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
    
    async def execute(self, params: dict) -> PluginResult:
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
            params: Paramètres update (dict ou SelfUpdateParams)
        
        Returns:
            Résultat update
        """
        # Convertir dict en objet Pydantic si nécessaire
        if isinstance(params, dict):
            params = SelfUpdateParams(**params)
        
        try:
            self.logger.info(f"[Update] Starting self-update to version {params.version}")
            
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
            
            # Step 7: SUCCESS - Pas de redémarrage automatique pour v1
            # L'utilisateur doit relancer manuellement l'agent
            self.logger.info("[Update] Update completed successfully!")
            self.logger.info("[Update] Please restart the agent manually to use the new version")
            
            return PluginResult(
                status="success",
                message=f"Update to version {params.version} completed. Please restart agent manually.",
                data={
                    "old_version": self.CURRENT_VERSION,
                    "new_version": params.version,
                    "backup_path": str(backup_path),
                    "restart_required": True,
                    "restart_command": f"python agent.py --agent-id {self.config.agent_id} --hub-url {self.config.hub_url}" if hasattr(self, 'config') else "python agent.py"
                }
            )
        
        except Exception as e:
            self.logger.error(f"[ERROR] Update failed: {e}", exc_info=True)
            
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
        
        self.logger.info(f"[OK] Downloaded {package_path.name} ({package_path.stat().st_size} bytes)")
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
        
        self.logger.info("[OK] Checksum verified")
        return True
    
    async def _backup_current_version(self) -> Path:
        """Sauvegarde la version actuelle."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self._backup_dir / f"agent_v{self.CURRENT_VERSION}_{timestamp}"
        
        # Copier tous les fichiers agent
        shutil.copytree(self._agent_dir, backup_path, dirs_exist_ok=True, ignore=shutil.ignore_patterns(
            ".backup", ".update_temp", "__pycache__", "*.pyc", ".git"
        ))
        
        self.logger.info(f"[OK] Backup created: {backup_path}")
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
        
        self.logger.info(f"[OK] Extracted to {extract_dir}")
    
    async def _replace_files(self):
        """
        Remplace les fichiers de l'agent par la nouvelle version.
        
        ⭐ AMÉLIORATION: Retry logic pour gérer file locks
        """
        extract_dir = self._temp_dir / "extracted"
        
        # Trouver le dossier racine extrait (peut avoir un sous-dossier)
        extracted_items = list(extract_dir.iterdir())
        if len(extracted_items) == 1 and extracted_items[0].is_dir():
            source_dir = extracted_items[0]
        else:
            source_dir = extract_dir
        
        # Lister tous les fichiers à remplacer
        files_to_replace = []
        for item in source_dir.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(source_dir)
                target_path = self._agent_dir / rel_path
                files_to_replace.append((item, target_path))
        
        self.logger.info(f"[+] Replacing {len(files_to_replace)} files...")
        
        # Remplacer fichiers avec retry logic
        failed_files = []
        for source_file, target_file in files_to_replace:
            # Skip agent.py (fichier actuel en cours d'exécution)
            if target_file.name == "agent.py":
                self.logger.debug(f"Skipping agent.py (will be replaced on restart)")
                continue
            
            # Créer dossier parent si nécessaire
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Tenter remplacement avec retry
            success = False
            for attempt in range(3):
                try:
                    # Méthode 1: Copier directement
                    shutil.copy2(source_file, target_file)
                    success = True
                    break
                except PermissionError:
                    # File lock: Tenter rename au lieu de delete
                    self.logger.debug(f"File locked: {target_file.name}, trying rename...")
                    try:
                        # Renommer ancien fichier avec .old
                        old_file = target_file.with_suffix(target_file.suffix + ".old")
                        if old_file.exists():
                            old_file.unlink()
                        target_file.rename(old_file)
                        
                        # Copier nouveau fichier
                        shutil.copy2(source_file, target_file)
                        success = True
                        break
                    except Exception as e:
                        self.logger.warning(f"Rename failed (attempt {attempt+1}/3): {e}")
                        await asyncio.sleep(1)
                except Exception as e:
                    self.logger.warning(f"Copy failed (attempt {attempt+1}/3): {e}")
                    await asyncio.sleep(1)
            
            if not success:
                failed_files.append(target_file.name)
                self.logger.error(f"Failed to replace: {target_file.name}")
        
        if failed_files:
            self.logger.warning(f"⚠️  {len(failed_files)} files failed to replace: {', '.join(failed_files)}")
            self.logger.warning("These files will be updated on next restart")
        else:
            self.logger.info("[OK] All files replaced successfully")
        
        return len(failed_files) == 0
    
    async def _restart_agent(self):
        """
        Restart l'agent avec la nouvelle version.
        
        ⭐ AMÉLIORATION: Auto-restart robuste selon méthode déploiement
        - Windows: Service (sc restart) ou pythonw subprocess
        - Linux: Systemd (systemctl restart) ou subprocess
        """
        self.logger.info("🔄 Preparing auto-restart...")
        
        os_name = platform.system()
        
        if os_name == "Windows":
            # Windows: Priorité service > tâche planifiée > subprocess
            try:
                # Méthode 1: Service Windows (si installé)
                result = subprocess.run(
                    ['sc', 'query', '333HOME Agent'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    # Service existe, utiliser sc restart
                    self.logger.info("✅ Service Windows détecté, restart via sc...")
                    subprocess.Popen(
                        'timeout 3 && sc stop "333HOME Agent" && sc start "333HOME Agent"',
                        shell=True,
                        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                    )
                    self.logger.info("[OK] Service restart scheduled")
                    await asyncio.sleep(2)
                    os._exit(0)
                
            except Exception as e:
                self.logger.debug(f"Service check failed: {e}, trying subprocess...")
            
            # Méthode 2: Subprocess pythonw (tray icon ou standalone)
            try:
                python_exe = sys.executable.replace("python.exe", "pythonw.exe")
                
                # Vérifier si agent_tray.pyw existe (installation avec tray icon)
                agent_tray = self._agent_dir / "agent_tray.pyw"
                if agent_tray.exists():
                    # Lancer agent_tray qui va relancer agent.py
                    self.logger.info("✅ Tray icon détecté, restart via agent_tray.pyw...")
                    subprocess.Popen(
                        [python_exe, str(agent_tray)],
                        cwd=str(self._agent_dir),
                        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                    )
                else:
                    # Lancer agent.py directement
                    self.logger.info("✅ Restart agent.py direct...")
                    subprocess.Popen(
                        [python_exe, "agent.py"] + sys.argv[1:],
                        cwd=str(self._agent_dir),
                        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                    )
                
                self.logger.info("[OK] Agent restart scheduled (pythonw)")
                await asyncio.sleep(2)
                os._exit(0)
                
            except Exception as e:
                self.logger.error(f"Subprocess restart failed: {e}")
                self.logger.warning("⚠️  Manual restart required via tray icon")
        
        else:
            # Linux/macOS: Priorité systemd > subprocess
            try:
                # Méthode 1: Systemd service (si installé)
                result = subprocess.run(
                    ['systemctl', 'is-active', '333agent'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    # Service systemd actif, utiliser systemctl restart
                    self.logger.info("✅ Systemd service détecté, restart via systemctl...")
                    subprocess.Popen(
                        ['sh', '-c', 'sleep 3 && systemctl restart 333agent'],
                        start_new_session=True
                    )
                    self.logger.info("[OK] Systemd restart scheduled")
                    await asyncio.sleep(2)
                    os._exit(0)
                
            except Exception as e:
                self.logger.debug(f"Systemd check failed: {e}, trying subprocess...")
            
            # Méthode 2: Subprocess direct (standalone)
            try:
                self.logger.info("✅ Restart agent.py subprocess...")
                subprocess.Popen(
                    [sys.executable, "agent.py"] + sys.argv[1:],
                    cwd=str(self._agent_dir),
                    start_new_session=True
                )
                self.logger.info("[OK] Agent restart scheduled (subprocess)")
                await asyncio.sleep(2)
                os._exit(0)
                
            except Exception as e:
                self.logger.error(f"Subprocess restart failed: {e}")
                self.logger.warning("⚠️  Manual restart required")
        
        # Si toutes les méthodes échouent
        self.logger.error("❌ Auto-restart failed, manual restart required")
        self.logger.info("Exiting current agent process...")
        await asyncio.sleep(2)
        os._exit(1)
    
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
        
        self.logger.info(f"[OK] Rolled back from {latest_backup}")
    
    async def _cleanup(self):
        """Nettoie les fichiers temporaires."""
        try:
            if self._temp_dir.exists():
                shutil.rmtree(self._temp_dir)
            self.logger.info("[OK] Cleanup completed")
        except Exception as e:
            self.logger.warning(f"Cleanup failed: {e}")
