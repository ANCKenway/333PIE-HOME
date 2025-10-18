"""
🏠 333HOME - Serveur HTTP Principal
Serveur simple et robuste pour la gestion de parc informatique
"""

import http.server
import socketserver
import json
import urllib.parse
from pathlib import Path

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import *
from core.models import ApiResponse
from core.database import db

class HomeAutomationHandler(http.server.BaseHTTPRequestHandler):
    """Handler HTTP pour 333HOME"""
    
    def log_message(self, format, *args):
        """Log personnalisé"""
        print(f"🌐 {self.address_string()} - {format % args}")
    
    def do_GET(self):
        """Gestion des requêtes GET"""
        path = self.path.split('?')[0]
        
        # ===== PAGES WEB =====
        if path == '/' or path == '/index.html':
            self._serve_file(WEB_DIR / 'index.html', 'text/html')
        
        # ===== FICHIERS STATIQUES =====
        elif path.startswith('/styles/'):
            file_path = WEB_DIR / path[1:]  # Enlever le /
            self._serve_static_file(file_path)
        elif path.startswith('/scripts/'):
            file_path = WEB_DIR / path[1:]
            self._serve_static_file(file_path)
        elif path.startswith('/assets/'):
            file_path = WEB_DIR / path[1:]
            self._serve_static_file(file_path)
        
        # ===== API ROUTES =====
        elif path == '/api/status':
            self._handle_api_status()
        elif path == '/api/devices':
            self._handle_api_devices()
        elif path == '/api/devices/favorites':
            self._handle_api_favorites()
        elif path == '/api/test':
            self._handle_api_test()
        
        # ===== NETWORK SCANNER API =====
        elif path == '/api/network/interfaces':
            self._handle_network_interfaces()
        elif path == '/api/network/scan':
            self._handle_network_scan()
        elif path == '/api/network/scan/quick':
            self._handle_network_quick_scan()
        elif path == '/api/network/devices':
            self._handle_network_devices()
        elif path.startswith('/api/network/device/'):
            self._handle_network_device_info()
        elif path.startswith('/api/network/vendor/'):
            self._handle_network_vendor()
        elif path == '/api/network/export':
            self._handle_network_export()
        elif path == '/api/network/statistics':
            self._handle_network_statistics()
        
        # ===== 404 =====
        else:
            self._send_404()
    
    def do_POST(self):
        """Gestion des requêtes POST"""
        path = self.path.split('?')[0]
        
        if path == '/api/test':
            self._handle_api_test_post()
        elif path == '/api/network/scan':
            self._handle_network_scan_post()
        elif path == '/api/network/device/add':
            self._handle_network_add_device()
        else:
            self._send_404()
    
    def _serve_file(self, file_path: Path, content_type: str):
        """Servir un fichier"""
        try:
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self._send_404()
        except Exception as e:
            print(f"❌ Erreur servir fichier {file_path}: {e}")
            self._send_500(str(e))
    
    def _serve_static_file(self, file_path: Path):
        """Servir un fichier statique avec bon content-type"""
        content_types = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon'
        }
        
        content_type = content_types.get(file_path.suffix.lower(), 'text/plain')
        self._serve_file(file_path, content_type)
    
    def _send_json_response(self, data: dict, status_code: int = 200):
        """Envoyer une réponse JSON"""
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(json_data.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))
    
    def _send_404(self):
        """Envoyer erreur 404"""
        message = "Page non trouvée"
        self.send_response(404)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
    
    def _send_500(self, error: str):
        """Envoyer erreur 500"""
        self.send_response(500)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(f"Erreur serveur: {error}".encode('utf-8'))
    
    # ===== HANDLERS API =====
    
    def _handle_api_status(self):
        """API: Statut de l'application"""
        response = ApiResponse(
            success=True,
            message="333HOME opérationnel",
            data={
                "app_name": APP_NAME,
                "version": APP_VERSION,
                "description": APP_DESCRIPTION,
                "server": f"{SERVER_HOST}:{SERVER_PORT}",
                "debug": DEBUG_MODE
            }
        )
        self._send_json_response(response.to_dict())
    
    def _handle_api_devices(self):
        """API: Liste des appareils"""
        try:
            devices = db.get_devices()
            devices_data = [device.to_dict() for device in devices]
            
            response = ApiResponse(
                success=True,
                message=f"{len(devices)} appareils trouvés",
                data={
                    "devices": devices_data,
                    "total": len(devices)
                }
            )
            self._send_json_response(response.to_dict())
            
        except Exception as e:
            response = ApiResponse(
                success=False,
                error=f"Erreur récupération appareils: {e}"
            )
            self._send_json_response(response.to_dict(), 500)
    
    def _handle_api_favorites(self):
        """API: Appareils favoris"""
        try:
            favorites = db.get_favorite_devices()
            favorites_data = [device.to_dict() for device in favorites]
            
            response = ApiResponse(
                success=True,
                message=f"{len(favorites)} favoris trouvés",
                data={
                    "favorites": favorites_data,
                    "total": len(favorites)
                }
            )
            self._send_json_response(response.to_dict())
            
        except Exception as e:
            response = ApiResponse(
                success=False,
                error=f"Erreur récupération favoris: {e}"
            )
            self._send_json_response(response.to_dict(), 500)
    
    def _handle_api_test(self):
        """API: Test de base"""
        response = ApiResponse(
            success=True,
            message="Test API réussi",
            data={
                "method": "GET",
                "timestamp": self._get_timestamp(),
                "client_ip": self.client_address[0]
            }
        )
        self._send_json_response(response.to_dict())
    
    def _handle_api_test_post(self):
        """API: Test POST"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            response = ApiResponse(
                success=True,
                message="Test POST réussi",
                data={
                    "method": "POST",
                    "received_bytes": len(post_data),
                    "timestamp": self._get_timestamp()
                }
            )
            self._send_json_response(response.to_dict())
            
        except Exception as e:
            response = ApiResponse(
                success=False,
                error=f"Erreur POST: {e}"
            )
            self._send_json_response(response.to_dict(), 500)
    
    def _get_timestamp(self):
        """Timestamp actuel"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # ===== NETWORK SCANNER API HANDLERS =====
    
    def _handle_network_interfaces(self):
        """API: Récupérer les interfaces réseau"""
        try:
            from modules.network import network_api
            result = network_api.get_network_interfaces()
            self._send_json_response(result)
        except Exception as e:
            response = ApiResponse(success=False, error=f"Erreur interfaces: {e}")
            self._send_json_response(response.to_dict(), 500)
    
    def _handle_network_scan(self):
        """API: Scanner le réseau (GET - scan rapide)"""
        try:
            from modules.network import network_api
            query_params = urllib.parse.parse_qs(self.path.split('?')[1] if '?' in self.path else '')
            
            network = query_params.get('network', [None])[0]
            include_ports = query_params.get('include_ports', ['false'])[0].lower() == 'true'
            
            if include_ports:
                result = network_api.scan_network(network, include_ports)
            else:
                result = network_api.quick_scan(network)
            
            self._send_json_response(result)
        except Exception as e:
            response = ApiResponse(success=False, error=f"Erreur scan: {e}")
            self._send_json_response(response.to_dict(), 500)
    
    def _handle_network_quick_scan(self):
        """API: Scan rapide du réseau"""
        try:
            from modules.network import network_api
            query_params = urllib.parse.parse_qs(self.path.split('?')[1] if '?' in self.path else '')
            network = query_params.get('network', [None])[0]
            
            result = network_api.quick_scan(network)
            self._send_json_response(result)
        except Exception as e:
            response = ApiResponse(success=False, error=f"Erreur scan rapide: {e}")
            self._send_json_response(response.to_dict(), 500)
    
    def _handle_network_scan_post(self):
        """API: Scanner le réseau (POST - scan avancé)"""
        try:
            from modules.network import network_api
            
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
            else:
                data = {}
            
            network = data.get('network')
            include_ports = data.get('include_ports', True)
            
            result = network_api.scan_network(network, include_ports)
            self._send_json_response(result)
            
        except Exception as e:
            response = ApiResponse(success=False, error=f"Erreur scan POST: {e}")
            self._send_json_response(response.to_dict(), 500)
    
    def _handle_network_devices(self):
        """API: Récupérer les appareils découverts"""
        try:
            from modules.network import network_api
            result = network_api.get_scan_history()
            self._send_json_response(result)
        except Exception as e:
            response = ApiResponse(success=False, error=f"Erreur récupération appareils: {e}")
            self._send_json_response(response.to_dict(), 500)
    
    def _handle_network_device_info(self):
        """API: Info d'un appareil spécifique"""
        try:
            from modules.network import network_api
            
            # Extraire l'identifier de l'URL (/api/network/device/192.168.1.10)
            path_parts = self.path.split('/')
            if len(path_parts) >= 5:
                identifier = path_parts[4].split('?')[0]  # Enlever les query params
                
                # Déterminer si c'est une IP ou MAC
                if ':' in identifier and len(identifier) == 17:
                    result = network_api.get_device_info(identifier, 'mac')
                else:
                    result = network_api.get_device_info(identifier, 'ip')
                
                self._send_json_response(result)
            else:
                response = ApiResponse(success=False, error="Identifier manquant")
                self._send_json_response(response.to_dict(), 400)
                
        except Exception as e:
            response = ApiResponse(success=False, error=f"Erreur info appareil: {e}")
            self._send_json_response(response.to_dict(), 500)
    
    def _handle_network_vendor(self):
        """API: Info fabricant MAC"""
        try:
            from modules.network import network_api
            
            # Extraire le MAC de l'URL (/api/network/vendor/AA:BB:CC:DD:EE:FF)
            path_parts = self.path.split('/')
            if len(path_parts) >= 5:
                mac = path_parts[4].split('?')[0]
                result = network_api.get_vendor_info(mac)
                self._send_json_response(result)
            else:
                response = ApiResponse(success=False, error="MAC manquant")
                self._send_json_response(response.to_dict(), 400)
                
        except Exception as e:
            response = ApiResponse(success=False, error=f"Erreur vendor: {e}")
            self._send_json_response(response.to_dict(), 500)
    
    def _handle_network_export(self):
        """API: Exporter les résultats"""
        try:
            from modules.network import network_api
            query_params = urllib.parse.parse_qs(self.path.split('?')[1] if '?' in self.path else '')
            format_type = query_params.get('format', ['json'])[0]
            
            result = network_api.export_scan_results(format_type)
            self._send_json_response(result)
        except Exception as e:
            response = ApiResponse(success=False, error=f"Erreur export: {e}")
            self._send_json_response(response.to_dict(), 500)
    
    def _handle_network_statistics(self):
        """API: Statistiques réseau"""
        try:
            from modules.network import network_api
            
            scan_history = network_api.get_scan_history()
            cache_stats = network_api.get_cache_stats()
            
            statistics = {
                "scan_available": scan_history['success'] and scan_history['data'] is not None,
                "cache_stats": cache_stats['data'] if cache_stats['success'] else {}
            }
            
            if scan_history['success'] and scan_history['data']:
                last_scan = scan_history['data']['last_scan']
                if 'device_analysis' in last_scan:
                    statistics['device_analysis'] = last_scan['device_analysis']
                if 'statistics' in last_scan:
                    statistics['scan_stats'] = last_scan['statistics']
            
            result = ApiResponse(success=True, data=statistics)
            self._send_json_response(result.to_dict())
            
        except Exception as e:
            response = ApiResponse(success=False, error=f"Erreur statistiques: {e}")
            self._send_json_response(response.to_dict(), 500)
    
    def _handle_network_add_device(self):
        """API: Ajouter un appareil à la gestion"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                device_data = json.loads(post_data.decode('utf-8'))
                
                # Validation basique
                required_fields = ['ip', 'name']
                for field in required_fields:
                    if field not in device_data:
                        response = ApiResponse(success=False, error=f"Champ requis manquant: {field}")
                        self._send_json_response(response.to_dict(), 400)
                        return
                
                # TODO: Intégrer avec le système de gestion des appareils
                response = ApiResponse(
                    success=True,
                    message=f"Appareil {device_data['name']} ajouté à la gestion",
                    data=device_data
                )
                self._send_json_response(response.to_dict())
            else:
                response = ApiResponse(success=False, error="Données manquantes")
                self._send_json_response(response.to_dict(), 400)
                
        except Exception as e:
            response = ApiResponse(success=False, error=f"Erreur ajout appareil: {e}")
            self._send_json_response(response.to_dict(), 500)

def start_server():
    """Démarrer le serveur"""
    print(f"🚀 Démarrage {APP_NAME} v{APP_VERSION}")
    print(f"📁 Dossier: {BASE_DIR}")
    print(f"🌐 Serveur: http://{SERVER_HOST}:{SERVER_PORT}")
    
    try:
        with socketserver.TCPServer((SERVER_HOST, SERVER_PORT), HomeAutomationHandler) as httpd:
            print(f"✅ Serveur démarré sur le port {SERVER_PORT}")
            print("🔗 Accès local: http://localhost:8000")
            print("🛑 Arrêt: Ctrl+C")
            print("=" * 50)
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur demandé")
    except Exception as e:
        print(f"❌ Erreur serveur: {e}")
    finally:
        print("✅ Serveur arrêté")

if __name__ == "__main__":
    start_server()