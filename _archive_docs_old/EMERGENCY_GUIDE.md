# 🔧 Guide d'Urgence 333HOME

## 🚨 EN CAS DE PROBLÈME CRITIQUE

### ⚠️ RAPPEL IMPORTANT
**🚧 Ce projet est en développement actif et l'architecture est un "champ de mine" !**
- Les solutions d'urgence peuvent ne pas fonctionner
- Le code peut être instable
- En cas de problème majeur, redémarrer complètement le système

---

## 🆘 Problèmes Critiques

### 1. Le Service Ne Démarre Pas

**🔥 Symptômes :**
```bash
# Service fails ou ne répond pas
sudo systemctl status 333home.service
● 333home.service - 333HOME Automation Service
   Loaded: loaded (/etc/systemd/system/333home.service; enabled; vendor preset: enabled)
   Active: failed (Result: exit-code) since ...
```

**🚑 Actions Immédiates :**
```bash
# 1. Arrêter complètement le service
sudo systemctl stop 333home.service

# 2. Vérifier les logs d'erreur
sudo journalctl -u 333home.service -f --no-pager

# 3. Redémarrer manuellement pour debug
cd /home/pie333/333HOME
python3 app.py

# 4. Si problème de dépendances
pip3 install -r requirements.txt --force-reinstall

# 5. Redémarrer le service
sudo systemctl start 333home.service
```

### 2. Erreur "Port Already in Use"

**🔥 Symptômes :**
```
OSError: [Errno 98] Address already in use: Port 8000
```

**🚑 Actions Immédiates :**
```bash
# Trouver le processus utilisant le port 8000
sudo lsof -i :8000

# Arrêter le processus (remplacer PID)
sudo kill -9 <PID>

# Ou arrêter tous les processus Python
sudo pkill -f "python.*app.py"

# Redémarrer le service
sudo systemctl restart 333home.service
```

### 3. Interface Web Ne Répond Pas

**🔥 Symptômes :**
- Page blanche ou erreur 502/503
- Impossible d'accéder à http://192.168.1.XXX:8000

**🚑 Actions Immédiates :**
```bash
# 1. Vérifier si le service tourne
sudo systemctl status 333home.service

# 2. Vérifier les logs en temps réel
sudo journalctl -u 333home.service -f

# 3. Test direct de l'API
curl http://localhost:8000/api/system/status

# 4. Redémarrage complet
sudo systemctl restart 333home.service

# 5. Si problème persiste, redémarrer le Pi
sudo reboot
```

### 4. Erreur "Module Not Found"

**🔥 Symptômes :**
```
ModuleNotFoundError: No module named 'fastapi'
ImportError: cannot import name 'NetworkScanner'
```

**🚑 Actions Immédiates :**
```bash
# 1. Réinstaller toutes les dépendances
cd /home/pie333/333HOME
pip3 install -r requirements.txt --force-reinstall

# 2. Vérifier l'environnement Python
python3 -c "import sys; print(sys.path)"

# 3. Si problème de modules locaux, vérifier PYTHONPATH
export PYTHONPATH="/home/pie333/333HOME:$PYTHONPATH"

# 4. Redémarrer le service
sudo systemctl restart 333home.service
```

---

## 🔄 Redémarrages d'Urgence

### Redémarrage Doux
```bash
# Arrêt propre du service
sudo systemctl stop 333home.service
sleep 5
sudo systemctl start 333home.service
```

### Redémarrage Forcé
```bash
# Arrêt forcé de tous les processus
sudo pkill -f "python.*333HOME"
sudo pkill -f "uvicorn"

# Nettoyage des ports
sudo fuser -k 8000/tcp

# Redémarrage du service
sudo systemctl restart 333home.service
```

### Redémarrage Complet Système
```bash
# ⚠️ Redémarrage complet du Raspberry Pi
sudo reboot
```

---

## 📊 Diagnostic Rapide

### Scripts de Vérification d'Urgence

**🔍 Check Status Script :**
```bash
#!/bin/bash
# Créer: ~/check_333home.sh

echo "=== 333HOME STATUS CHECK ==="
echo "Date: $(date)"
echo

echo "--- Service Status ---"
sudo systemctl status 333home.service --no-pager

echo
echo "--- Process Check ---"
ps aux | grep -E "(python.*app.py|uvicorn)" | grep -v grep

echo
echo "--- Port Check ---"
sudo lsof -i :8000

echo
echo "--- Recent Logs ---"
sudo journalctl -u 333home.service --since "10 minutes ago" --no-pager

echo
echo "--- API Test ---"
curl -s http://localhost:8000/api/system/status | head -20

echo
echo "=== END STATUS CHECK ==="
```

**Utilisation :**
```bash
chmod +x ~/check_333home.sh
~/check_333home.sh
```

### Vérification de l'Intégrité des Fichiers

```bash
# Vérifier que les fichiers critiques existent
ls -la /home/pie333/333HOME/app.py
ls -la /home/pie333/333HOME/requirements.txt
ls -la /etc/systemd/system/333home.service

# Vérifier les permissions
ls -la /home/pie333/333HOME/

# Vérifier la structure des dossiers
tree /home/pie333/333HOME/ -L 2
```

---

## 🔒 Récupération de Configuration

### Sauvegarde d'Urgence
```bash
# Créer une sauvegarde rapide
cd /home/pie333/
tar -czf "333HOME_backup_$(date +%Y%m%d_%H%M%S).tar.gz" 333HOME/

# Sauvegarder seulement la config
cp -r 333HOME/config/ ~/config_backup_$(date +%Y%m%d_%H%M%S)/
```

### Restauration des Configurations par Défaut
```bash
# ⚠️ ATTENTION: Ceci efface les configurations personnalisées

# Sauvegarder d'abord
cp -r /home/pie333/333HOME/config/ ~/config_backup_emergency/

# Restaurer config par défaut (si disponible)
cd /home/pie333/333HOME
git checkout config/devices.json
# ou créer un devices.json vide
echo '{"devices": [], "last_updated": "'$(date -Iseconds)'"}' > config/devices.json
```

---

## 🌐 Problèmes Réseau d'Urgence

### Perte de Connectivité

**🔍 Diagnostic :**
```bash
# Vérifier la connectivité de base
ping -c 3 8.8.8.8
ping -c 3 192.168.1.1

# Vérifier les interfaces réseau
ip addr show
ip route show

# Vérifier si le service peut écouter
sudo netstat -tlnp | grep :8000
```

**🚑 Solutions :**
```bash
# Redémarrer la stack réseau
sudo systemctl restart networking

# Ou redémarrer NetworkManager
sudo systemctl restart NetworkManager

# Renouveler l'IP
sudo dhclient -r && sudo dhclient
```

### Problèmes avec l'API Tailscale

**🚑 Actions :**
```bash
# Vérifier statut Tailscale
sudo tailscale status

# Redémarrer Tailscale
sudo systemctl restart tailscaled

# Désactiver temporairement Tailscale
sudo tailscale down

# Réactiver
sudo tailscale up
```

---

## 📞 Contacts d'Urgence et Ressources

### 🔗 Ressources de Debug
- **Logs Système :** `/var/log/syslog`
- **Logs 333HOME :** `sudo journalctl -u 333home.service`
- **Config Systemd :** `/etc/systemd/system/333home.service`

### 📝 Informations à Collecter
En cas de problème, collecter ces informations :

```bash
# Script de collecte d'info d'urgence
echo "=== 333HOME EMERGENCY INFO ===" > ~/333home_debug.log
echo "Date: $(date)" >> ~/333home_debug.log
echo "Hostname: $(hostname)" >> ~/333home_debug.log
echo "Uptime: $(uptime)" >> ~/333home_debug.log
echo >> ~/333home_debug.log

echo "--- System Info ---" >> ~/333home_debug.log
cat /etc/os-release >> ~/333home_debug.log
echo >> ~/333home_debug.log

echo "--- Service Status ---" >> ~/333home_debug.log
sudo systemctl status 333home.service --no-pager >> ~/333home_debug.log 2>&1
echo >> ~/333home_debug.log

echo "--- Recent Logs ---" >> ~/333home_debug.log
sudo journalctl -u 333home.service --since "1 hour ago" --no-pager >> ~/333home_debug.log 2>&1
echo >> ~/333home_debug.log

echo "--- Process Info ---" >> ~/333home_debug.log
ps aux | grep -E "(python|uvicorn)" >> ~/333home_debug.log
echo >> ~/333home_debug.log

echo "--- Network Info ---" >> ~/333home_debug.log
ip addr show >> ~/333home_debug.log
sudo lsof -i :8000 >> ~/333home_debug.log 2>&1
echo >> ~/333home_debug.log

echo "=== END EMERGENCY INFO ===" >> ~/333home_debug.log

echo "Debug info saved to: ~/333home_debug.log"
```

---

## ⚠️ Notes Importantes

### 🚧 Limitations Actuelles
1. **Architecture instable** - Les solutions peuvent ne pas fonctionner
2. **Code expérimental** - Comportements imprévisibles possibles
3. **Monitoring limité** - Diagnostics basiques seulement
4. **Pas de rollback automatique** - Récupération manuelle nécessaire

### 🎯 Future - Intégration 333srv
- Les procédures d'urgence évolueront avec l'intégration au serveur principal
- Monitoring centralisé prévu
- Récupération automatique planifiée
- Diagnostics avancés via 333srv

### 📋 Checklist Post-Incident
Après résolution d'un problème :

- [ ] Documenter la cause du problème
- [ ] Mettre à jour cette documentation
- [ ] Vérifier que le monitoring fonctionne
- [ ] Tester les fonctionnalités principales
- [ ] Planifier des améliorations préventives

---

**⚠️ Rappel :** En cas de problème majeur, ne pas hésiter à redémarrer complètement le système. Le projet étant en développement, la stabilité n'est pas garantie.

**📅 Dernière mise à jour :** 19 octobre 2025  
**🔄 Version :** Procédures d'urgence v1.0  
**🎯 Statut :** Adapté pour architecture expérimentale