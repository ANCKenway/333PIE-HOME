"""
📝 333HOME - Configuration du logging structuré
Logging moderne avec formatage et niveaux configurables
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Formateur avec couleurs pour le terminal"""
    
    # Codes couleur ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Vert
        'WARNING': '\033[33m',    # Jaune
        'ERROR': '\033[31m',      # Rouge
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Ajouter couleur au niveau
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_format: Optional[str] = None,
    log_file: Optional[Path] = None,
    colorize: bool = True
) -> None:
    """
    Configure le système de logging
    
    Args:
        level: Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format des messages de log
        log_file: Fichier de sortie optionnel
        colorize: Activer les couleurs dans la console
    """
    
    # Format par défaut
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Niveau de logging
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configuration du logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Nettoyer les handlers existants
    root_logger.handlers.clear()
    
    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    if colorize:
        console_formatter = ColoredFormatter(log_format)
    else:
        console_formatter = logging.Formatter(log_format)
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Handler fichier (si spécifié)
    if log_file:
        log_file.parent.mkdir(exist_ok=True, parents=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Réduire le niveau de logging des bibliothèques tierces
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    logging.info(f"✅ Logging configuré - Niveau: {level}")
    if log_file:
        logging.info(f"📁 Logs fichier: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Obtenir un logger pour un module spécifique
    
    Args:
        name: Nom du module
    
    Returns:
        Logger configuré
    """
    return logging.getLogger(name)


class LogContext:
    """Context manager pour logs temporaires avec contexte"""
    
    def __init__(self, logger: logging.Logger, context: str, level: int = logging.INFO):
        self.logger = logger
        self.context = context
        self.level = level
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.log(self.level, f"▶️ {self.context} - Début")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.log(self.level, f"✅ {self.context} - Terminé ({duration:.2f}s)")
        else:
            self.logger.error(f"❌ {self.context} - Erreur ({duration:.2f}s): {exc_val}")
        
        return False  # Propager l'exception


# Raccourcis pour contextes de log
def log_operation(logger: logging.Logger, operation: str):
    """Créer un contexte de log pour une opération"""
    return LogContext(logger, operation, logging.INFO)


def log_debug_operation(logger: logging.Logger, operation: str):
    """Créer un contexte de log debug pour une opération"""
    return LogContext(logger, operation, logging.DEBUG)
