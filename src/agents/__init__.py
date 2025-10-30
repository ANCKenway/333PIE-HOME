"""
333HOME Agents Module
=====================

Architecture modulaire pour agents de contrôle à distance multi-OS.

Structure:
    - agent.py: Agent universel cross-platform (WebSocket persistent)
    - plugins/: Système de plugins extensible
        - base.py: Classes abstraites BasePlugin
        - windows/: Plugins Windows (LogMeIn, RDP, PowerShell...)
        - linux/: Plugins Linux (SSH, Docker, Systemd...)
        - common/: Plugins cross-platform (system_info, monitoring...)
    - deployments/: Scripts et configs déploiement (PyInstaller, Docker)

Priorité Windows (TITO) pour Phase 1, architecture extensible Linux (333srv).
"""

__version__ = "1.0.0"
__author__ = "333HOME Team"
