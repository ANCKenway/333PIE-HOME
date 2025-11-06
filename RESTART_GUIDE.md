# 🔄 Redémarrage à distance - 333HOME

## 🎯 Solutions disponibles

### 1️⃣ **Page de redémarrage d'urgence** (Recommandé)

**URL** : `http://192.168.1.150:8000/restart` (ou via IP Tailscale)

✅ **Avantages** :
- Simple, accessible depuis n'importe quel navigateur
- Fonctionne même si l'interface principale plante
- Bouton unique : "Redémarrer le serveur"
- Rechargement automatique après 10 secondes

📱 **Utilisation** :
1. Ouvrir `http://IP:8000/restart` dans un navigateur
2. Cliquer sur "🔄 Redémarrer le serveur"
3. Confirmer
4. Attendre 10 secondes → redirection automatique

---

### 2️⃣ **Service Systemd** (Le plus robuste)

**Installation** :
```bash
cd /home/pie333/333HOME
./install_systemd.sh
systemctl --user enable 333home
```

**Contrôle via Cockpit (interface web)** :
1. Installer Cockpit : `sudo apt install cockpit`
2. Accéder : `http://192.168.1.150:9090`
3. Onglet "Services" → Chercher "333home"
4. Boutons Start/Stop/Restart disponibles

**Commandes SSH (si besoin)** :
```bash
systemctl --user restart 333home   # Redémarrer
systemctl --user stop 333home      # Arrêter
systemctl --user start 333home     # Démarrer
systemctl --user status 333home    # Statut
```

---

### 3️⃣ **Via API REST** (Pour automatisation)

**Endpoint** : `POST http://192.168.1.150:8000/api/system/restart`

**Exemple curl** :
```bash
curl -X POST http://192.168.1.150:8000/api/system/restart
```

**Exemple depuis un autre script** :
```python
import requests
response = requests.post("http://192.168.1.150:8000/api/system/restart")
print(response.json())
```

---

### 4️⃣ **Via application mobile** (Avec Cockpit)

Installer l'app mobile Cockpit :
- **Android** : [Cockpit Client](https://play.google.com/store/apps/details?id=com.cockpit.client)
- **iOS** : Utiliser Safari vers `http://IP:9090`

Permet de contrôler le service depuis votre téléphone n'importe où (via Tailscale).

---

## 🚨 Scénarios d'urgence

### Scénario 1 : Interface web freeze
1. Ouvrir `/restart` dans un nouvel onglet
2. Cliquer "Redémarrer"
3. ✅ Serveur redémarre proprement

### Scénario 2 : Serveur complètement planté
1. Ouvrir Cockpit : `http://IP:9090`
2. Services → 333home → Restart
3. ✅ Systemd force le redémarrage

### Scénario 3 : Vous êtes à distance (pas de SSH)
1. **Option A** : Via Tailscale → `/restart` sur IP VPN
2. **Option B** : Via Cockpit mobile
3. **Option C** : Via API REST depuis un script

---

## 📝 Ordre de priorité recommandé

1. **Page `/restart`** → Plus simple, toujours accessible
2. **Cockpit** → Si vous voulez une vraie interface d'administration
3. **Systemd manual** → Si SSH disponible
4. **API REST** → Pour automatisation/scripts

---

## 🔒 Sécurité

⚠️ **Important** : 
- L'endpoint `/api/system/restart` n'a **pas d'authentification** actuellement
- Recommandé : Mettre derrière Tailscale (déjà le cas)
- Optionnel : Ajouter un mot de passe simple dans `restart.html`

**Pour ajouter un mot de passe simple** :
Éditer `web/restart.html`, ligne ~94, remplacer :
```javascript
const confirmed = confirm('⚠️ Êtes-vous sûr...');
```
Par :
```javascript
const password = prompt('🔐 Mot de passe :');
if (password !== 'VotreMotDePasse') {
    alert('❌ Mot de passe incorrect');
    return;
}
const confirmed = confirm('⚠️ Êtes-vous sûr...');
```

---

## ✅ Installation rapide

```bash
# 1. Installer le service systemd
cd /home/pie333/333HOME
chmod +x install_systemd.sh
./install_systemd.sh
systemctl --user enable 333home

# 2. (Optionnel) Installer Cockpit
sudo apt install cockpit
sudo systemctl enable --now cockpit.socket

# 3. Tester la page de redémarrage
# Ouvrir dans un navigateur : http://192.168.1.150:8000/restart
```

**C'est tout !** Vous pouvez maintenant redémarrer le serveur à distance sans SSH.

---

## 📱 Accès depuis votre téléphone

1. **Via Tailscale** : `http://100.x.x.x:8000/restart`
2. **Sur réseau local** : `http://192.168.1.150:8000/restart`
3. **Via Cockpit** : `http://100.x.x.x:9090` (app mobile ou navigateur)

Ajoutez en raccourci sur l'écran d'accueil pour un accès rapide ! 📲
