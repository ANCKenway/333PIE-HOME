# 🔧 Résolution de Problèmes 333HOME

## 🎯 Objectif
Guide complet pour diagnostiquer et résoudre les problèmes courants de 333HOME.

## 🚨 Problèmes Courants et Solutions

### 🔴 Problème 1 : Application ne démarre pas

#### Symptômes
```bash
$ python app_new.py
ModuleNotFoundError: No module named 'fastapi'
```

#### Diagnostic
```bash
# Vérifier Python
python --version

# Vérifier les dépendances
pip list | grep fastapi
pip list | grep uvicorn

# Vérifier la structure
ls -la api/
ls -la modules/
```

#### Solutions
```bash
# Installation des dépendances
pip install -r requirements.txt

# Si problème persistant
pip install --upgrade fastapi uvicorn

# Vérifier les imports
python -c "import fastapi; print('FastAPI OK')"
```

### 🔴 Problème 2 : Import Errors Backend

#### Symptômes
```bash
ImportError: cannot import name 'DeviceManager' from 'modules.devices'
```

#### Diagnostic
```bash
# Vérifier la structure des modules
find modules/ -name "*.py" -exec echo "=== {} ===" \; -exec head -5 {} \;

# Vérifier les __init__.py
find . -name "__init__.py" -exec ls -la {} \;

# Test import direct
python -c "from modules.devices import DeviceManager; print('OK')"
```

#### Solutions
```bash
# Créer les __init__.py manquants
touch modules/__init__.py
touch modules/devices/__init__.py
touch modules/network/__init__.py

# Vérifier le PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Alternative : installation en mode développement
pip install -e .
```

### 🔴 Problème 3 : Interface Web Cassée

#### Symptômes
- Page blanche
- Erreurs JavaScript dans la console
- Styles CSS non appliqués

#### Diagnostic
```bash
# Vérifier les fichiers statiques
ls -la web/static/js/
ls -la web/static/css/

# Test serveur statique
curl http://localhost:8000/static/js/app.js
curl http://localhost:8000/static/css/main.css

# Console navigateur (F12)
# Rechercher les erreurs 404 ou JS
```

#### Solutions
```bash
# Vérifier la configuration FastAPI
grep -n "StaticFiles" app_new.py

# Corriger les permissions
chmod -R 644 web/static/

# Vider le cache navigateur
# Ctrl+F5 ou mode incognito

# Test direct des modules
python -c "
import os
print(os.path.exists('web/static/js/app.js'))
print(os.path.exists('web/static/css/main.css'))
"
```

### 🔴 Problème 4 : API Endpoints Non Fonctionnels

#### Symptômes
```bash
$ curl http://localhost:8000/api/devices/
{"detail":"Not Found"}
```

#### Diagnostic
```bash
# Tester l'endpoint de base
curl http://localhost:8000/api/status

# Vérifier les routes chargées
curl http://localhost:8000/docs

# Tester individuellement
curl http://localhost:8000/api/devices/
curl http://localhost:8000/api/network/scan
curl http://localhost:8000/api/monitoring/stats
```

#### Solutions
```python
# Vérifier l'inclusion des routers dans app_new.py
# Doit contenir :
from api.router import main_router
app.include_router(main_router)

# Vérifier api/router.py
# Doit inclure tous les sous-routers

# Test des imports
python -c "
from api.routes.devices import router
print('Devices router OK')
"
```

### 🔴 Problème 5 : Scan Réseau Échoue

#### Symptômes
- Scan ne trouve aucun appareil
- Erreurs de timeout
- Permissions insuffisantes

#### Diagnostic
```bash
# Test ping manuel
ping -c 1 192.168.1.1

# Test nmap (si installé)
nmap -sn 192.168.1.0/24

# Vérifier les permissions
id
groups

# Test des modules réseau
python -c "
from modules.network import NetworkScanner
scanner = NetworkScanner()
print('Scanner OK')
"
```

#### Solutions
```bash
# Installer nmap si nécessaire
sudo apt-get install nmap

# Permissions pour ping
sudo setcap cap_net_raw+ep $(which ping)

# Alternative : utiliser les scripts avec sudo
sudo python app_new.py

# Configurer scan moins agressif
# Dans le code : timeout plus long, moins de ports
```

### 🔴 Problème 6 : Configuration Tailscale

#### Symptômes
- VPN non configuré
- Erreurs d'authentification
- Appareils non détectés

#### Diagnostic
```bash
# Vérifier la config Tailscale
ls -la config/
cat config/tailscale.json 2>/dev/null || echo "Pas de config"

# Test API Tailscale
curl -H "Authorization: Bearer tskey-auth-xxxxx" \
     "https://api.tailscale.com/api/v2/tailnet/mon-tailnet/devices"

# Vérifier les services
systemctl status tailscaled 2>/dev/null || echo "Tailscale non installé"
```

#### Solutions
```bash
# Installer Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Configurer via l'interface web
# Aller sur http://localhost:8000/
# Section Services > Tailscale

# Configuration manuelle
mkdir -p config
echo '{
  "tailnet": "votre-tailnet.ts.net",
  "api_key": "tskey-auth-xxxxx"
}' > config/tailscale.json
```

## 🛠️ Outils de Diagnostic

### 📊 Script de Diagnostic Complet
```bash
#!/bin/bash
# diagnostic.sh - Script de diagnostic 333HOME

echo "🔍 Diagnostic 333HOME"
echo "===================="

echo "📋 Environnement:"
python --version
pip --version
echo "OS: $(uname -a)"

echo "📁 Structure:"
ls -la app*.py
ls -la api/ 2>/dev/null || echo "❌ Dossier api/ manquant"
ls -la modules/ 2>/dev/null || echo "❌ Dossier modules/ manquant"
ls -la web/ 2>/dev/null || echo "❌ Dossier web/ manquant"

echo "📦 Dépendances:"
pip list | grep -E "(fastapi|uvicorn|httpx|psutil)"

echo "🌐 Connectivité:"
ping -c 1 8.8.8.8 > /dev/null && echo "✅ Internet OK" || echo "❌ Pas d'internet"
ping -c 1 192.168.1.1 > /dev/null && echo "✅ Réseau local OK" || echo "❌ Réseau local KO"

echo "🔧 Ports:"
netstat -tuln | grep :8000 && echo "✅ Port 8000 utilisé" || echo "⚠️ Port 8000 libre"

echo "📄 Logs récents:"
tail -5 debug.log 2>/dev/null || echo "Pas de logs debug"

echo "🎯 Test imports:"
python -c "
try:
    from api.router import main_router
    print('✅ Router principal OK')
except Exception as e:
    print(f'❌ Router principal: {e}')

try:
    from modules.devices import DeviceManager
    print('✅ DeviceManager OK')
except Exception as e:
    print(f'❌ DeviceManager: {e}')

try:
    from modules.network import NetworkScanner
    print('✅ NetworkScanner OK')
except Exception as e:
    print(f'❌ NetworkScanner: {e}')
"

echo "🔍 Diagnostic terminé"
```

### 🔧 Réparation Express
```bash
#!/bin/bash
# repair.sh - Réparation rapide 333HOME

echo "🔧 Réparation 333HOME"
echo "==================="

# Arrêter les processus existants
echo "🔴 Arrêt des processus..."
pkill -f "python.*app"

# Nettoyer les caches
echo "🧹 Nettoyage caches..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# Recréer les __init__.py
echo "📁 Recréation __init__.py..."
touch modules/__init__.py
touch modules/devices/__init__.py
touch modules/network/__init__.py
touch modules/services/__init__.py
touch api/__init__.py
touch api/routes/__init__.py

# Réinstaller les dépendances
echo "📦 Réinstallation dépendances..."
pip install --force-reinstall -r requirements.txt

# Vérifier les permissions
echo "🔐 Permissions..."
chmod +x start.sh stop.sh
chmod -R 644 web/static/

# Test final
echo "🧪 Test final..."
python -c "
import sys
sys.path.insert(0, '.')
from api.router import main_router
print('✅ Réparation réussie')
" && echo "🎉 Application prête" || echo "❌ Problème persistant"
```

## 📝 Logs et Monitoring

### 📊 Activation des Logs Détaillés
```python
# Dans app_new.py, modifier le niveau de log
logging.basicConfig(
    level=logging.DEBUG,  # Plus de détails
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
```

### 🔍 Surveillance Temps Réel
```bash
# Logs en temps réel
tail -f debug.log

# Monitoring réseau
watch -n 5 'netstat -tuln | grep :8000'

# Monitoring processus
watch -n 5 'ps aux | grep python'

# Monitoring mémoire
watch -n 10 'free -h'
```

## 🚨 Procédures d'Urgence

### 🔴 Rollback d'Urgence
```bash
# Si l'architecture modulaire pose problème
echo "🚨 ROLLBACK D'URGENCE"

# Utiliser l'ancien app.py monolithique
mv app.py app_legacy.py
mv app_new.py app_new_broken.py
mv app_legacy.py app.py

# Démarrer en mode legacy
python app.py

echo "⚠️ Application en mode legacy - Corriger l'architecture modulaire"
```

### 🔧 Reset Complet
```bash
# Reset total du projet
git stash  # Sauvegarder les modifications
git reset --hard HEAD  # Retour au dernier commit
git clean -fd  # Nettoyer les fichiers non suivis

# Réinstallation complète
pip install -r requirements.txt
python app_new.py
```

## 📋 Checklist de Résolution

### ✅ Avant de Demander de l'Aide
- [ ] Script de diagnostic exécuté
- [ ] Logs consultés (debug.log)
- [ ] Imports testés individuellement
- [ ] Permissions vérifiées
- [ ] Cache vidé
- [ ] Réseaux testés
- [ ] Documentation consultée

### 🔍 Informations à Fournir
1. **Système** : OS, Python version, hardware
2. **Erreur exacte** : Message complet, stack trace
3. **Contexte** : Que faisiez-vous quand l'erreur est survenue ?
4. **Reproduction** : Étapes pour reproduire le problème
5. **Logs** : Extraits pertinents de debug.log
6. **Tests** : Résultats du script de diagnostic

## 📞 Support et Ressources

### 📚 Documentation
- [Architecture](./ARCHITECTURE.md) - Comprendre la structure
- [Guide Développement](./DEVELOPMENT_GUIDE.md) - Processus de dev
- [API Documentation](./API_DOCUMENTATION.md) - Endpoints détaillés

### 🔧 Outils Externes
- **FastAPI Docs** : http://localhost:8000/docs
- **Postman** : Test des APIs
- **Browser DevTools** : Debug frontend
- **htop/top** : Monitoring système

### 🆘 En Dernier Recours
Si aucune solution ne fonctionne :
1. Sauvegarder vos données (`config/`, `data/`)
2. Clone fresh du repository
3. Restaurer vos données
4. Reprendre depuis la documentation

---

**📅 Guide créé :** 19 octobre 2025  
**🔧 Couverture :** Problèmes courants + procédures d'urgence  
**🎯 Objectif :** Résolution autonome des problèmes