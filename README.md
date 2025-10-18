# Home Automation - Raspberry Pi

Application de domotique pour contrôler vos appareils domestiques depuis votre Raspberry Pi.

## Fonctionnalités

- 🖥️ **Wake-on-LAN** : Démarrez vos PC à distance
- 🎬 **Contrôle Plex** : Gérez votre serveur multimédia
- 🌐 **Monitoring réseau** : Surveillez vos appareils connectés
- 📱 **Interface mobile** : Contrôlez depuis votre téléphone
- 🔒 **Sécurisé** : Authentification pour protéger l'accès

## Installation

1. Clonez ce projet sur votre Raspberry Pi
2. Installez les dépendances : `pip install -r requirements.txt`
3. Configurez vos appareils dans `config/devices.json`
4. Lancez l'application : `python main.py`
5. Accédez à l'interface : `http://votre-pi:8000`

## Configuration

Modifiez le fichier `config/devices.json` pour ajouter vos appareils :

```json
{
  "computers": [
    {
      "name": "PC Bureau",
      "ip": "192.168.1.100",
      "mac": "AA:BB:CC:DD:EE:FF"
    }
  ],
  "services": [
    {
      "name": "Plex",
      "host": "192.168.1.100",
      "port": 32400
    }
  ]
}
```

## Utilisation

- Accédez au dashboard via votre navigateur
- Utilisez les boutons pour contrôler vos appareils
- Surveillez l'état de vos services en temps réel

## Développement

Pour développer ou modifier l'application :

```bash
# Mode développement avec rechargement automatique
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Support

Ce projet est optimisé pour Raspberry Pi sous Linux avec Python 3.7+.