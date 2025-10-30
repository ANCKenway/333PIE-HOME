"""
333HOME Agent - Tray Icon Wrapper
==================================

Wrapper avec icône dans la barre des tâches pour contrôler l'agent facilement.

Fonctionnalités:
- Lance l'agent en arrière-plan (subprocess)
- Icône tray avec menu contextuel
- Statut connexion en temps réel
- Gestion logs, restart, settings
- Notifications Windows

Usage:
    pythonw agent_tray.pyw  (pas de console)
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Optional

import psutil
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem, Menu

# Import découverte Hub
try:
    from hub_discovery import discover_hub
    HUB_DISCOVERY_AVAILABLE = True
except ImportError:
    HUB_DISCOVERY_AVAILABLE = False
    print("Warning: hub_discovery module not found, using static config")

# Configuration
AGENT_SCRIPT = Path(__file__).parent / "agent.py"
CONFIG_FILE = Path(__file__).parent / "tray_config.json"
LOG_FILE = Path(__file__).parent / "logs" / "agent_stdout.log"

# Couleurs icône
COLOR_CONNECTED = (76, 175, 80)      # Vert
COLOR_DISCONNECTED = (244, 67, 54)   # Rouge
COLOR_STARTING = (255, 193, 7)       # Jaune


class AgentTray:
    """Gestionnaire icône tray pour l'agent."""
    
    def __init__(self):
        self.agent_process: Optional[subprocess.Popen] = None
        self.connected = False
        self.agent_id = "Unknown"
        self.hub_url = "Unknown"
        self.icon: Optional[pystray.Icon] = None
        self.running = True
        
        # Charger config
        self.load_config()
        
        # Créer dossier logs si nécessaire
        LOG_FILE.parent.mkdir(exist_ok=True)
    
    def load_config(self):
        """Charge la configuration."""
        if CONFIG_FILE.exists():
            try:
                # utf-8-sig pour gérer le BOM UTF-8 de PowerShell
                with open(CONFIG_FILE, 'r', encoding='utf-8-sig') as f:
                    config = json.load(f)
                    self.agent_id = config.get('agent_id', os.environ.get('COMPUTERNAME', 'Unknown'))
                    
                    # Hub URL: auto-découverte OU config manuelle
                    if config.get('auto_discover_hub', True) and HUB_DISCOVERY_AVAILABLE:
                        print("🔍 Auto-découverte du Hub activée...")
                        self.hub_url = discover_hub()
                    else:
                        self.hub_url = config.get('hub_url', 'ws://100.115.207.11:8000/api/ws/agents')
            except Exception as e:
                print(f"Error loading config: {e}")
                # Fallback sur valeurs par défaut avec auto-découverte
                self.agent_id = os.environ.get('COMPUTERNAME', 'Unknown')
                if HUB_DISCOVERY_AVAILABLE:
                    self.hub_url = discover_hub()
                else:
                    self.hub_url = 'ws://100.115.207.11:8000/api/ws/agents'
        else:
            # Config par défaut avec auto-découverte
            self.agent_id = os.environ.get('COMPUTERNAME', 'Unknown')
            if HUB_DISCOVERY_AVAILABLE:
                self.hub_url = discover_hub()
            else:
                self.hub_url = 'ws://100.115.207.11:8000/api/ws/agents'
            self.save_config()
    
    def save_config(self):
        """Sauvegarde la configuration."""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump({
                    'agent_id': self.agent_id,
                    'hub_url': self.hub_url
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def create_icon_image(self, color: tuple) -> Image.Image:
        """Crée l'image de l'icône avec la couleur spécifiée."""
        # Créer image 64x64
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), (255, 255, 255))
        dc = ImageDraw.Draw(image)
        
        # Dessiner cercle coloré
        margin = 8
        dc.ellipse(
            (margin, margin, width - margin, height - margin),
            fill=color,
            outline=(0, 0, 0)
        )
        
        # Dessiner "H" au centre (pour Home)
        dc.text((width//2 - 8, height//2 - 12), "H", fill=(255, 255, 255))
        
        return image
    
    def update_icon(self):
        """Met à jour l'icône selon l'état."""
        if self.icon:
            if self.agent_process and self.agent_process.poll() is None:
                # Agent running
                color = COLOR_CONNECTED if self.connected else COLOR_DISCONNECTED
            else:
                # Agent stopped
                color = COLOR_DISCONNECTED
            
            self.icon.icon = self.create_icon_image(color)
    
    def start_agent(self):
        """Démarre l'agent."""
        if self.agent_process and self.agent_process.poll() is None:
            print("Agent already running")
            return
        
        print(f"Starting agent: {self.agent_id}")
        
        # Arguments agent
        args = [
            sys.executable,
            str(AGENT_SCRIPT),
            '--agent-id', self.agent_id,
            '--hub-url', self.hub_url,
            '--log-level', 'INFO'
        ]
        
        try:
            # Créer fichiers logs
            log_dir = Path(__file__).parent / "logs"
            log_dir.mkdir(exist_ok=True)
            stdout_log = log_dir / "agent_stdout.log"
            stderr_log = log_dir / "agent_stderr.log"
            
            # Ouvrir fichiers logs en mode append
            stdout_file = open(stdout_log, 'a', encoding='utf-8')
            stderr_file = open(stderr_log, 'a', encoding='utf-8')
            
            # Lancer agent en subprocess (sans console)
            if sys.platform == 'win32':
                # Windows: utiliser pythonw pour cacher console
                pythonw = sys.executable.replace('python.exe', 'pythonw.exe')
                if Path(pythonw).exists():
                    args[0] = pythonw
                
                # CREATE_NO_WINDOW flag
                self.agent_process = subprocess.Popen(
                    args,
                    stdout=stdout_file,
                    stderr=stderr_file,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                self.agent_process = subprocess.Popen(
                    args,
                    stdout=stdout_file,
                    stderr=stderr_file
                )
            
            print(f"Agent started (PID: {self.agent_process.pid})")
            self.update_icon()
            
        except Exception as e:
            print(f"Failed to start agent: {e}")
    
    def stop_agent(self):
        """Arrête l'agent."""
        if not self.agent_process:
            print("Agent not running")
            return
        
        print(f"Stopping agent (PID: {self.agent_process.pid})")
        
        try:
            # Terminer proprement
            self.agent_process.terminate()
            
            # Attendre 5s max
            try:
                self.agent_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Forcer kill si nécessaire
                self.agent_process.kill()
                self.agent_process.wait()
            
            print("Agent stopped")
            self.agent_process = None
            self.connected = False
            self.update_icon()
            
        except Exception as e:
            print(f"Failed to stop agent: {e}")
    
    def restart_agent(self):
        """Redémarre l'agent."""
        print("Restarting agent...")
        self.stop_agent()
        time.sleep(1)
        self.start_agent()
    
    def check_agent_status(self):
        """Vérifie le statut de l'agent via les logs."""
        try:
            if not LOG_FILE.exists():
                self.connected = False
                return
            
            # Lire dernières lignes du log
            with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                recent_lines = lines[-20:] if len(lines) > 20 else lines
            
            # Chercher indicateurs de connexion
            for line in reversed(recent_lines):
                if '[OK] Connected to Hub' in line:
                    self.connected = True
                    return
                elif 'Connection closed' in line or 'Failed to connect' in line:
                    self.connected = False
                    return
            
        except Exception as e:
            print(f"Error checking status: {e}")
    
    def monitor_loop(self):
        """Boucle de monitoring en arrière-plan."""
        while self.running:
            # Vérifier si processus agent encore actif
            if self.agent_process:
                if self.agent_process.poll() is not None:
                    # Agent crashed
                    print("Agent process died, restarting...")
                    self.agent_process = None
                    time.sleep(2)
                    self.start_agent()
            
            # Vérifier statut connexion
            self.check_agent_status()
            
            # Mettre à jour icône
            self.update_icon()
            
            # Attendre 5s
            time.sleep(5)
    
    def view_logs(self, icon, item):
        """Ouvre le fichier de logs."""
        if LOG_FILE.exists():
            # Ouvrir avec notepad
            os.startfile(LOG_FILE)
        else:
            print("Log file not found")
    
    def restart(self, icon, item):
        """Redémarre l'agent."""
        self.restart_agent()
    
    def settings(self, icon, item):
        """Ouvre les paramètres (simple dialog)."""
        # TODO: Implémenter dialog graphique avec tkinter
        print("Settings dialog not implemented yet")
        print(f"Current config:")
        print(f"  Agent ID: {self.agent_id}")
        print(f"  Hub URL: {self.hub_url}")
    
    def about(self, icon, item):
        """Affiche les informations."""
        msg = f"333HOME Agent\n\n"
        msg += f"Agent ID: {self.agent_id}\n"
        msg += f"Hub URL: {self.hub_url}\n"
        msg += f"Status: {'Connected' if self.connected else 'Disconnected'}\n"
        
        if self.agent_process:
            msg += f"PID: {self.agent_process.pid}\n"
        
        print(msg)
        # TODO: Afficher dans dialog Windows
    
    def quit_app(self, icon, item):
        """Quitte l'application."""
        print("Quitting...")
        self.running = False
        self.stop_agent()
        icon.stop()
    
    def create_menu(self) -> Menu:
        """Crée le menu contextuel."""
        return Menu(
            MenuItem(
                lambda item: f"{'🟢' if self.connected else '🔴'} {self.agent_id}",
                lambda icon, item: None,
                enabled=False
            ),
            Menu.SEPARATOR,
            MenuItem('View Logs', self.view_logs),
            MenuItem('Restart Agent', self.restart),
            Menu.SEPARATOR,
            MenuItem('Settings', self.settings),
            MenuItem('About', self.about),
            Menu.SEPARATOR,
            MenuItem('Quit', self.quit_app)
        )
    
    def run(self):
        """Lance l'application tray."""
        print("Starting 333HOME Agent Tray...")
        
        # Démarrer agent
        self.start_agent()
        
        # Démarrer thread monitoring
        monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        monitor_thread.start()
        
        # Créer icône tray
        self.icon = pystray.Icon(
            name="333HOME Agent",
            icon=self.create_icon_image(COLOR_STARTING),
            title=f"333HOME Agent - {self.agent_id}",
            menu=self.create_menu()
        )
        
        # Lancer boucle icône (blocking)
        print("Tray icon started")
        self.icon.run()
        
        print("Tray icon stopped")


def main():
    """Point d'entrée principal."""
    try:
        app = AgentTray()
        app.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
