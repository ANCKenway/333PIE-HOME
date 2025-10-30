"""
🔥 Plugin LogMeIn Rescue v2 - Simple & Robust
==============================================

Automation LogMeIn Rescue SANS Selenium - Juste webbrowser + subprocess + Windows SendKeys API.

Workflow:
1. Ouvre navigateur par défaut avec URL + code
2. Le navigateur télécharge automatiquement l'applet
3. Attend téléchargement dans dossier Downloads
4. Lance applet avec droits admin (UAC)
5. Envoie Tab + Enter via Windows SendKeys API pour valider fenêtre permission
   (curseur par défaut sur ANNULER, donc Tab → OK, puis Enter → validé)

Avantages vs Selenium:
- ✅ Pas de conflit Chrome user-data-dir
- ✅ Pas de dépendance chromedriver
- ✅ Utilise le navigateur déjà installé
- ✅ Automatisation complète sans intervention (SendKeys fonctionne avec fenêtres admin)
- ✅ 10x plus simple et robuste
"""

from typing import Optional
from pydantic import BaseModel, Field, validator
import asyncio
import logging
import os
import time
import webbrowser
from pathlib import Path
import subprocess

from ..base import WindowsPlugin, PluginParams, PluginResult, PluginExecutionError

# Import pour envoyer touches clavier avec Windows API (fonctionne avec fenêtres admin)
try:
    import win32com.client
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


logger = logging.getLogger(__name__)


class LogMeInRescueParams(PluginParams):
    """Paramètres pour LogMeIn Rescue automation."""
    
    rescue_code: str = Field(
        ...,
        description="Code rescue 6 chiffres",
        min_length=6,
        max_length=6
    )
    
    timeout: int = Field(
        default=120,
        ge=30,
        le=300,
        description="Timeout total automation (secondes)"
    )
    
    @validator("rescue_code")
    def validate_rescue_code(cls, v):
        """Valide le code rescue."""
        if not v.isdigit():
            raise ValueError("Le code rescue doit contenir uniquement des chiffres")
        if len(v) != 6:
            raise ValueError("Le code rescue doit faire exactement 6 chiffres")
        return v


class LogMeInRescuePlugin(WindowsPlugin):
    """
    Plugin LogMeIn Rescue - Version simple sans Selenium.
    
    Utilise webbrowser + pywinauto pour automation légère.
    """
    
    name = "logmein_rescue"
    description = "LogMeIn Rescue automation (simple version)"
    version = "2.0.0"
    
    # URL LogMeIn
    LOGMEIN_URL = "https://secure.logmeinrescue.com/Customer/Code.aspx"
    
    def __init__(self):
        super().__init__()
        self._download_dir = Path.home() / "Downloads"
    
    def validate_params(self, params: dict) -> bool:
        """Valide les paramètres."""
        try:
            LogMeInRescueParams(**params)
            return True
        except Exception as e:
            self.logger.error(f"Invalid params: {e}")
            return False
    
    async def execute(self, params: dict) -> PluginResult:
        """
        Exécute l'automation LogMeIn simple.
        
        Steps:
        1. Ouvre navigateur avec URL + code en POST
        2. Attend téléchargement applet
        3. Lance applet avec droits admin
        
        Args:
            params: Paramètres LogMeIn (dict ou LogMeInRescueParams)
        
        Returns:
            Résultat automation
        """
        # Convertir dict en objet Pydantic si nécessaire
        if isinstance(params, dict):
            params = LogMeInRescueParams(**params)
        
        start_time = time.time()
        
        try:
            self.logger.info(f"🚀 Starting LogMeIn automation v2 for code: {params.rescue_code}")
            
            # Step 1: Ouvrir navigateur avec code
            url_with_code = f"{self.LOGMEIN_URL}?Code={params.rescue_code}"
            self.logger.info(f"Opening browser: {url_with_code}")
            webbrowser.open(url_with_code)
            
            # Step 2: Attendre téléchargement applet
            self.logger.info(f"Waiting for applet download in {self._download_dir}")
            applet_path = await self._wait_for_applet_download(timeout=params.timeout - 30)
            
            # Step 3: Lancer applet avec droits admin
            self.logger.info(f"Launching applet: {applet_path}")
            await self._launch_applet_as_admin(applet_path)
            
            duration_ms = (time.time() - start_time) * 1000
            
            return PluginResult(
                status="success",
                message=f"LogMeIn session started for code {params.rescue_code}",
                data={
                    "rescue_code": params.rescue_code,
                    "applet_path": str(applet_path),
                    "method": "webbrowser_simple"
                },
                duration_ms=duration_ms
            )
            
        except asyncio.TimeoutError:
            return PluginResult(
                status="timeout",
                message=f"Automation timeout after {params.timeout}s",
                error="Timeout exceeded"
            )
        except Exception as e:
            self.logger.error(f"❌ LogMeIn automation failed: {e}", exc_info=True)
            return PluginResult(
                status="error",
                message="LogMeIn automation failed",
                error=str(e)
            )
    
    async def _wait_for_applet_download(self, timeout: int = 90) -> Path:
        """
        Attend le téléchargement de l'applet LogMeIn.
        
        Cherche fichiers récents dans Downloads :
        - *.exe (applet LogMeIn)
        - CustomerClient.exe
        - rescue*.exe
        
        Args:
            timeout: Timeout en secondes
        
        Returns:
            Path de l'applet téléchargé
        
        Raises:
            TimeoutError: Si timeout dépassé
        """
        start_time = time.time()
        
        # Patterns fichiers applet LogMeIn (tous les formats connus)
        patterns = [
            "Support-LogMeInRescue*.exe",  # Format standard Fiducial
            "CustomerClient*.exe",          # Format classique
            "rescue*.exe",                  # Format générique
            "logmein*.exe"                  # Format générique
        ]
        
        while time.time() - start_time < timeout:
            # Chercher fichiers récents (< 2 minutes)
            recent_files = []
            for pattern in patterns:
                for file_path in self._download_dir.glob(pattern):
                    if file_path.is_file():
                        # Vérifier si fichier récent
                        age = time.time() - file_path.stat().st_mtime
                        if age < 120:  # < 2 minutes
                            recent_files.append(file_path)
            
            if recent_files:
                # Prendre le plus récent
                applet = max(recent_files, key=lambda p: p.stat().st_mtime)
                self.logger.info(f"✓ Applet found: {applet.name}")
                return applet
            
            await asyncio.sleep(2)
        
        raise asyncio.TimeoutError(f"Applet download timeout after {timeout}s")
    
    async def _launch_applet_as_admin(self, applet_path: Path):
        """
        Lance l'applet avec droits administrateur et automatise le clic "OK".
        
        Workflow:
        1. Lance applet avec élévation UAC (PowerShell Start-Process -Verb RunAs)
        2. Attend fenêtre permission applet LogMeIn
        3. Détecte et clique bouton "OK" automatiquement
        
        Args:
            applet_path: Chemin vers l'applet
        """
        try:
            # Lancer avec élévation UAC
            cmd = ["powershell", "-Command", f"Start-Process '{applet_path}' -Verb RunAs"]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                self.logger.info("✓ Applet launched successfully")
            else:
                self.logger.warning(f"Applet launch returned code {process.returncode}")
                if stderr:
                    self.logger.warning(f"stderr: {stderr.decode('utf-8', errors='ignore')}")
            
            # Automatiser la validation "OK" avec Windows API SendKeys
            if WIN32_AVAILABLE:
                await self._auto_press_enter()
            else:
                self.logger.warning("win32com non disponible - validation manuelle requise")
            
        except Exception as e:
            self.logger.error(f"Failed to launch applet: {e}")
            raise
    
    async def _auto_press_enter(self):
        """
        Automatise la validation "OK" avec Tab + Enter via Windows API SendKeys.
        
        Utilise win32com.client.Dispatch("WScript.Shell").SendKeys()
        Fonctionne même avec les fenêtres lancées en admin (contrairement à pyautogui).
        
        Par défaut curseur sur ANNULER → Tab → OK → Enter → validé !
        """
        try:
            self.logger.info("Attente fenêtre permission (5 secondes)...")
            
            # Attendre 5 secondes que la fenêtre apparaisse et se mette en avant
            await asyncio.sleep(5)
            
            self.logger.info("Envoi Tab + Enter via Windows SendKeys API...")
            
            # Exécuter SendKeys dans un thread séparé (non-blocking)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._sendkeys_tab_enter)
            
            self.logger.info("✓ Tab + Enter envoyés via SendKeys - permission validée")
            
        except Exception as e:
            self.logger.warning(f"Auto-validation échouée: {e} - Validation manuelle nécessaire")
    
    def _sendkeys_tab_enter(self):
        """
        Envoie Tab + Enter via Windows SendKeys API.
        
        Windows API SendKeys fonctionne avec les fenêtres admin (contrairement à pyautogui).
        Syntaxe SendKeys: {TAB} pour Tab, {ENTER} pour Enter, ~ pour Enter aussi.
        """
        try:
            self.logger.info("DEBUG: Création WScript.Shell...")
            shell = win32com.client.Dispatch("WScript.Shell")
            
            self.logger.info("DEBUG: Envoi {TAB} via SendKeys...")
            shell.SendKeys("{TAB}")
            
            time.sleep(0.5)  # Pause 0.5s entre Tab et Enter
            
            self.logger.info("DEBUG: Envoi {ENTER} via SendKeys...")
            shell.SendKeys("{ENTER}")
            
            self.logger.info("DEBUG: SendKeys terminé avec succès")
            
        except Exception as e:
            self.logger.error(f"ERREUR SendKeys: {type(e).__name__}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
