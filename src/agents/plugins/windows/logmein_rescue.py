"""
🔥 Plugin LogMeIn Rescue - Windows (TITO)
==========================================

Automation complète LogMeIn Rescue pour télémaintenance TITO.

Fonctionnalités:
- Saisie code 6 chiffres
- Navigation https://secure.logmeinrescue.com/Customer/Code.aspx
- Téléchargement applet LogMeIn
- Lancement en mode administrateur (UAC bypass)
- Acceptation automatique tous droits

Priorité: 🔴 CRITIQUE (Phase 1)
"""

from typing import Optional
from pydantic import BaseModel, Field, validator
import asyncio
import logging
import os
import time
from pathlib import Path

from ..base import WindowsPlugin, PluginParams, PluginResult, PluginExecutionError


logger = logging.getLogger(__name__)


class LogMeInRescueParams(PluginParams):
    """Paramètres pour LogMeIn Rescue automation."""
    
    rescue_code: str = Field(
        ...,
        description="Code rescue 6 chiffres",
        min_length=6,
        max_length=6
    )
    
    headless: bool = Field(
        default=False,
        description="Lancer browser en mode headless (pas recommandé)"
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
    Plugin LogMeIn Rescue automation.
    
    Utilise Selenium WebDriver pour automatiser:
    1. Navigation vers page LogMeIn
    2. Saisie code 6 chiffres
    3. Téléchargement applet
    4. Lancement en admin
    5. Acceptation droits
    """
    
    name = "logmein_rescue"
    description = "Automation LogMeIn Rescue pour télémaintenance"
    version = "1.0.0"
    os_platform = "windows"
    
    LOGMEIN_URL = "https://secure.logmeinrescue.com/Customer/Code.aspx"
    
    def __init__(self):
        super().__init__()
        self._driver = None
        self._download_dir = None
    
    async def setup(self) -> bool:
        """Setup Selenium WebDriver."""
        try:
            # Import Selenium (lazy loading)
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            
            # Configuration download dir
            self._download_dir = Path(os.getenv("TEMP", "C:\\Temp")) / "logmein"
            self._download_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"LogMeIn plugin setup completed. Download dir: {self._download_dir}")
            return True
            
        except ImportError as e:
            self.logger.error(f"Failed to import Selenium: {e}")
            self.logger.error("Install: pip install selenium webdriver-manager")
            return False
        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False
    
    async def execute(self, params: LogMeInRescueParams) -> PluginResult:
        """
        Exécute l'automation LogMeIn Rescue complète.
        
        Steps:
        1. Ouvre browser Chrome
        2. Navigate to LogMeIn URL
        3. Enter rescue code
        4. Wait for applet download
        5. Launch applet as admin
        6. Accept all permissions
        
        Args:
            params: Paramètres LogMeIn (code rescue)
        
        Returns:
            Résultat automation
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"🚀 Starting LogMeIn automation for code: {params.rescue_code}")
            
            # Step 1: Setup WebDriver
            await self._setup_webdriver(params.headless)
            
            # Step 2: Navigate to LogMeIn
            self.logger.info(f"Navigating to {self.LOGMEIN_URL}")
            self._driver.get(self.LOGMEIN_URL)
            await asyncio.sleep(2)  # Wait for page load
            
            # Step 3: Enter rescue code
            await self._enter_rescue_code(params.rescue_code)
            
            # Step 4: Wait for download
            applet_path = await self._wait_for_download(timeout=params.timeout - 30)
            
            # Step 5: Launch as admin
            await self._launch_as_admin(applet_path)
            
            # Step 6: Auto-accept permissions
            await self._auto_accept_permissions()
            
            duration_ms = (time.time() - start_time) * 1000
            
            return PluginResult(
                status="success",
                message=f"LogMeIn session started successfully for code {params.rescue_code}",
                data={
                    "rescue_code": params.rescue_code,
                    "applet_path": str(applet_path),
                    "session_active": True
                },
                duration_ms=duration_ms
            )
            
        except asyncio.TimeoutError:
            return PluginResult(
                status="timeout",
                message=f"Automation timeout after {params.timeout}s",
                error="Timeout exceeded",
                duration_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            self.logger.error(f"❌ LogMeIn automation failed: {e}", exc_info=True)
            return PluginResult(
                status="error",
                message="Automation failed",
                error=str(e),
                duration_ms=(time.time() - start_time) * 1000
            )
            
        finally:
            # Cleanup
            await self._cleanup_webdriver()
    
    def validate_params(self, params: dict) -> bool:
        """Valide les paramètres."""
        try:
            LogMeInRescueParams(**params)
            return True
        except Exception as e:
            self.logger.error(f"Invalid params: {e}")
            return False
    
    def get_schema(self) -> dict:
        """Retourne le schéma des paramètres."""
        return LogMeInRescueParams.schema()
    
    async def _setup_webdriver(self, headless: bool = False):
        """Configure et démarre le WebDriver Chrome."""
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        
        if headless:
            options.add_argument("--headless")
        
        # Configuration download
        prefs = {
            "download.default_directory": str(self._download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False
        }
        options.add_experimental_option("prefs", prefs)
        
        # Disable automation flags
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        self.logger.info("Starting Chrome WebDriver...")
        self._driver = webdriver.Chrome(options=options)
        self._driver.set_page_load_timeout(30)
    
    async def _enter_rescue_code(self, code: str):
        """Entre le code rescue dans le formulaire."""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        self.logger.info(f"Entering rescue code: {code}")
        
        # Wait for input field
        wait = WebDriverWait(self._driver, 10)
        code_input = wait.until(
            EC.presence_of_element_located((By.ID, "txtCode"))
        )
        
        # Clear and enter code
        code_input.clear()
        code_input.send_keys(code)
        
        # Submit form
        submit_button = self._driver.find_element(By.ID, "btnSubmit")
        submit_button.click()
        
        self.logger.info("✓ Code submitted")
    
    async def _wait_for_download(self, timeout: int = 60) -> Path:
        """Attend le téléchargement de l'applet."""
        self.logger.info(f"Waiting for applet download (timeout: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check for .exe files in download dir
            exe_files = list(self._download_dir.glob("*.exe"))
            if exe_files:
                applet_path = exe_files[0]
                self.logger.info(f"✓ Applet downloaded: {applet_path}")
                return applet_path
            
            await asyncio.sleep(1)
        
        raise TimeoutError("Applet download timeout")
    
    async def _launch_as_admin(self, applet_path: Path):
        """Lance l'applet en mode administrateur (UAC bypass)."""
        self.logger.info(f"Launching {applet_path} as administrator...")
        
        if not self.is_admin:
            self.logger.warning("Not running as admin - UAC will prompt")
        
        # Launch with admin privileges (Windows ctypes)
        import ctypes
        
        try:
            result = ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",  # Verb for "Run as administrator"
                str(applet_path),
                None,
                str(applet_path.parent),
                1  # SW_SHOWNORMAL
            )
            
            if result > 32:  # Success
                self.logger.info("✓ Applet launched as admin")
                await asyncio.sleep(3)  # Wait for launch
            else:
                raise PluginExecutionError(f"Failed to launch applet (error code: {result})")
                
        except Exception as e:
            raise PluginExecutionError(f"Failed to elevate privileges: {e}")
    
    async def _auto_accept_permissions(self):
        """Accepte automatiquement toutes les permissions (pywinauto)."""
        self.logger.info("Auto-accepting permissions...")
        
        try:
            # Import pywinauto (lazy loading)
            from pywinauto import Application
            
            # Wait for LogMeIn window
            await asyncio.sleep(2)
            
            # Connect to LogMeIn app
            app = Application(backend="uia").connect(title_re=".*LogMeIn.*", timeout=10)
            
            # Find and click all "Accept"/"Allow"/"OK" buttons
            for window in app.windows():
                for button in window.children(control_type="Button"):
                    if any(text in button.window_text().lower() for text in ["accept", "allow", "ok", "continue"]):
                        self.logger.info(f"Clicking button: {button.window_text()}")
                        button.click()
                        await asyncio.sleep(0.5)
            
            self.logger.info("✓ Permissions accepted")
            
        except ImportError:
            self.logger.warning("pywinauto not installed - manual permission acceptance required")
            self.logger.warning("Install: pip install pywinauto")
        except Exception as e:
            self.logger.warning(f"Could not auto-accept permissions: {e}")
            # Non-fatal, user can accept manually
    
    async def _cleanup_webdriver(self):
        """Ferme le WebDriver."""
        if self._driver:
            try:
                self.logger.info("Closing WebDriver...")
                self._driver.quit()
                self._driver = None
            except Exception as e:
                self.logger.error(f"Error closing WebDriver: {e}")
    
    async def teardown(self) -> bool:
        """Nettoyage du plugin."""
        await self._cleanup_webdriver()
        return await super().teardown()
