#!/usr/bin/env python3
"""
🚀 Serveur Home Automation ULTRA PROPRE - Production Ready
Sans dépendances externes compliquées, juste du Python pur et efficace
"""

import http.server
import socketserver
import json
import urllib.parse
import threading
import time
import os
import sys
from pathlib import Path

# Import de nos modules
sys.path.append(str(Path(__file__).parent))
try:
    from modules.network.advanced_scanner import UltraNetworkScanner
    from modules.dashboard.service import UltraDashboardService
    print("✅ Modules importés avec succès")
except ImportError as e:
    print(f"❌ Erreur import modules: {e}")
    sys.exit(1)

class HomeAutomationHandler(http.server.BaseHTTPRequestHandler):
    """Handler HTTP ultra propre pour notre serveur"""
    
    # Services partagés (initialisés une seule fois)
    _scanner = None
    _dashboard_service = None
    
    @classmethod
    def init_services(cls):
        """Initialiser les services une seule fois"""
        if cls._scanner is None:
            print("🔥 Initialisation du scanner ultra blindé...")
            cls._scanner = UltraNetworkScanner()
        if cls._dashboard_service is None:
            print("📊 Initialisation du service dashboard...")
            cls._dashboard_service = UltraDashboardService()
    
    def __init__(self, *args, **kwargs):
        # Utilisation des services partagés
        self.scanner = self._scanner
        self.dashboard_service = self._dashboard_service
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Gestion des requêtes GET"""
        path = self.path.split('?')[0]  # Remove query params
        
        # Routes statiques (HTML, CSS, JS)
        if path == '/' or path == '/index.html':
            self.serve_file('web/templates/index.html', 'text/html')
        elif path.startswith('/static/'):
            self.serve_static_file(path)
        elif path.startswith('/css/'):
            # Rediriger /css/ vers /static/css/
            self.serve_static_file('/static' + path)
        elif path.startswith('/js/'):
            # Rediriger /js/ vers /static/js/
            self.serve_static_file('/static' + path)
        
        # API Routes - Dashboard
        elif path == '/api/dashboard/':
            self.handle_dashboard_api()
        
        # API Routes - Network
        elif path == '/api/network/discover':
            self.handle_network_discover()
        elif path == '/api/network/scan':
            self.handle_network_scan()
        elif path == '/api/network/scan/live':
            self.handle_network_scan_live()
        elif path == '/api/network/devices':
            self.handle_network_devices()
        elif path == '/api/network/stats':
            self.handle_network_stats()
        elif path == '/api/network/scan/result':
            self.handle_network_scan_result()
        
        # Routes des pages
        elif path in ['/dashboard', '/network', '/devices', '/monitoring']:
            self.serve_file('web/templates/index.html', 'text/html')
        
        else:
            self.send_404()
    
    def do_POST(self):
        """Gestion des requêtes POST"""
        path = self.path.split('?')[0]
        
        if path == '/api/network/scan':
            self.handle_network_scan()
        else:
            self.send_404()
    
    def serve_file(self, filepath, content_type):
        """Servir un fichier statique"""
        try:
            full_path = Path(__file__).parent / filepath
            if full_path.exists():
                with open(full_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_404()
        except Exception as e:
            print(f"❌ Erreur lecture fichier {filepath}: {e}")
            self.send_500(str(e))
    
    def serve_static_file(self, path):
        """Servir les fichiers statiques (CSS, JS, images)"""
        # Mapping des extensions vers content-type
        ext_map = {
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.ico': 'image/x-icon',
            '.svg': 'image/svg+xml'
        }
        
        filepath = 'web' + path
        file_path = Path(__file__).parent / filepath
        
        if file_path.exists():
            ext = file_path.suffix.lower()
            content_type = ext_map.get(ext, 'text/plain')
            self.serve_file(filepath, content_type)
        else:
            self.send_404()
    
    # API Handlers
    def handle_dashboard_api(self):
        """API Dashboard ultra"""
        try:
            data = self.dashboard_service.get_ultra_dashboard_data()
            self.send_json_response({"success": True, "data": data})
        except Exception as e:
            print(f"❌ Erreur dashboard API: {e}")
            self.send_json_response({"success": False, "error": str(e)})
    
    def handle_network_discover(self):
        """API Network discover"""
        try:
            # Scan rapide pour la découverte
            result = self.scanner.scan_network_ultra_blindé()
            devices = [device.__dict__ for device in result]
            
            stats = {
                "total_devices": len(devices),
                "online_devices": len([d for d in devices if d.get("status") == "online"]),
                "identified_vendor": len([d for d in devices if d.get("vendor") and d.get("vendor") != "unknown"])
            }
            
            self.send_json_response({
                "success": True,
                "data": {
                    "devices": devices,
                    "stats": stats,
                    "message": f"🔍 {len(devices)} appareils découverts"
                }
            })
        except Exception as e:
            print(f"❌ Erreur network discover: {e}")
            self.send_json_response({"success": False, "error": str(e)})
    
    def handle_network_scan(self):
        """API Network scan"""
        try:
            result = self.scanner.scan_network_ultra_blindé()
            devices = [device.__dict__ for device in result]
            
            stats = {
                "total_devices": len(devices),
                "online_devices": len([d for d in devices if d.get("status") == "online"]),
                "identified_vendor": len([d for d in devices if d.get("vendor") and d.get("vendor") != "unknown"])
            }
            
            response_data = {
                "devices": devices,
                "stats": stats,
                "timestamp": time.time(),
                "message": f"🔥 Scan ultra terminé: {len(devices)} appareils analysés"
            }
            
            self.send_json_response({
                "success": True, 
                "data": response_data,
                "message": response_data["message"]
            })
        except Exception as e:
            print(f"❌ Erreur network scan: {e}")
            self.send_json_response({"success": False, "error": str(e)})
    
    def handle_network_scan_live(self):
        """API Network scan live"""
        self.handle_network_scan()  # Same as regular scan for now
    
    def handle_network_devices(self):
        """API Network devices"""
        self.handle_network_scan()  # Same as scan
    
    def handle_network_stats(self):
        """API Network stats"""
        try:
            result = self.scanner.scan_network_ultra_blindé()
            devices = [device.__dict__ for device in result]
            
            stats = {
                "total_devices": len(devices),
                "online_devices": len([d for d in devices if d.get("status") == "online"]),
                "identified_vendor": len([d for d in devices if d.get("vendor") and d.get("vendor") != "unknown"]),
                "scan_quality": "ultra_blindé",
                "identification_rate": (len([d for d in devices if d.get("vendor") and d.get("vendor") != "unknown"]) / max(len(devices), 1)) * 100
            }
            
            self.send_json_response({"success": True, "data": stats})
        except Exception as e:
            print(f"❌ Erreur network stats: {e}")
            self.send_json_response({"success": False, "error": str(e)})
    
    def handle_network_scan_result(self):
        """API Network scan result"""
        self.handle_network_scan()  # Same as scan
    
    # Utility methods
    def send_json_response(self, data):
        """Envoyer une réponse JSON"""
        try:
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            json_bytes = json_data.encode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(json_bytes)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json_bytes)
        except Exception as e:
            print(f"❌ Erreur envoi JSON: {e}")
            self.send_500(str(e))
    
    def send_404(self):
        """Envoyer une erreur 404"""
        self.send_response(404)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>404 - Page non trouvée</title></head>
        <body>
            <h1>🚫 Erreur 404</h1>
            <p>La page demandée n'existe pas.</p>
            <p><a href="/">← Retour à l'accueil</a></p>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))
    
    def send_500(self, error):
        """Envoyer une erreur 500"""
        self.send_response(500)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        error_data = {"success": False, "error": f"Erreur serveur: {error}"}
        self.wfile.write(json.dumps(error_data).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Log custom pour nos besoins"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"🌐 {timestamp} - {format % args}")


class HomeAutomationServer:
    """Serveur Home Automation ultra propre"""
    
    def __init__(self, host='0.0.0.0', port=8000):
        self.host = host
        self.port = port
        self.httpd = None
        self.running = False
    
    def start(self):
        """Démarrer le serveur"""
        try:
            print(f"🚀 Démarrage serveur Home Automation ULTRA PROPRE")
            print(f"🌐 Adresse: http://{self.host}:{self.port}")
            print(f"📁 Dossier: {Path(__file__).parent}")
            print(f"🔥 Mode: PRODUCTION READY")
            print("=" * 60)
            
            # Initialisation des services
            HomeAutomationHandler.init_services()
            
            # Création du serveur HTTP
            with socketserver.TCPServer((self.host, self.port), HomeAutomationHandler) as self.httpd:
                self.httpd.allow_reuse_address = True
                self.running = True
                
                print(f"✅ Serveur démarré avec succès !")
                print(f"🔗 Interface: http://localhost:{self.port}")
                print(f"🔗 Dashboard: http://localhost:{self.port}/dashboard")
                print(f"🔗 Réseau: http://localhost:{self.port}/network")
                print("=" * 60)
                print("📋 Logs en temps réel:")
                
                # Servir indéfiniment
                self.httpd.serve_forever()
                
        except KeyboardInterrupt:
            print("\n🛑 Arrêt du serveur demandé par l'utilisateur")
            self.stop()
        except Exception as e:
            print(f"❌ Erreur serveur: {e}")
            self.stop()
    
    def stop(self):
        """Arrêter le serveur"""
        if self.httpd and self.running:
            print("🛑 Arrêt du serveur en cours...")
            self.httpd.shutdown()
            self.running = False
            print("✅ Serveur arrêté proprement")


def main():
    """Point d'entrée principal"""
    print("🚀 HOME AUTOMATION - SERVEUR ULTRA PROPRE")
    print("=" * 60)
    
    # Configuration
    HOST = '0.0.0.0'  # Accessible depuis le réseau
    PORT = 8000
    
    # Vérifications pré-démarrage
    web_dir = Path(__file__).parent / 'web'
    if not web_dir.exists():
        print(f"❌ Dossier web manquant: {web_dir}")
        sys.exit(1)
    
    modules_dir = Path(__file__).parent / 'modules'
    if not modules_dir.exists():
        print(f"❌ Dossier modules manquant: {modules_dir}")
        sys.exit(1)
    
    print("✅ Vérifications pré-démarrage OK")
    
    # Démarrage du serveur
    server = HomeAutomationServer(HOST, PORT)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par Ctrl+C")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
    finally:
        server.stop()


if __name__ == "__main__":
    main()