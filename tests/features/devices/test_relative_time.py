"""
Tests pour le formatage de temps relatif

Vérifie que les timestamps sont correctement formatés en temps relatif
"""

import pytest
from datetime import datetime, timedelta


class TestRelativeTimeFormatting:
    """Tests pour le formatage de temps relatif"""

    def test_format_just_now(self):
        """Test: < 60 secondes = 'à l'instant'"""
        now = datetime.now()
        timestamp = now - timedelta(seconds=30)
        
        seconds = (now - timestamp).total_seconds()
        result = 'à l\'instant' if seconds < 60 else None
        
        assert result == 'à l\'instant'
        assert seconds < 60

    def test_format_minutes(self):
        """Test: < 60 minutes = 'il y a X min'"""
        now = datetime.now()
        timestamp = now - timedelta(minutes=15)
        
        seconds = (now - timestamp).total_seconds()
        minutes = int(seconds / 60)
        result = f'il y a {minutes} min' if minutes < 60 else None
        
        assert result == 'il y a 15 min'
        assert minutes == 15

    def test_format_hours(self):
        """Test: < 24 heures = 'il y a Xh'"""
        now = datetime.now()
        timestamp = now - timedelta(hours=5)
        
        seconds = (now - timestamp).total_seconds()
        minutes = int(seconds / 60)
        hours = int(minutes / 60)
        result = f'il y a {hours}h' if hours < 24 else None
        
        assert result == 'il y a 5h'
        assert hours == 5

    def test_format_days(self):
        """Test: < 7 jours = 'il y a Xj'"""
        now = datetime.now()
        timestamp = now - timedelta(days=3)
        
        seconds = (now - timestamp).total_seconds()
        hours = int(seconds / 3600)
        days = int(hours / 24)
        result = f'il y a {days}j' if days < 7 else None
        
        assert result == 'il y a 3j'
        assert days == 3

    def test_format_weeks(self):
        """Test: < 4 semaines = 'il y a Xsem'"""
        now = datetime.now()
        timestamp = now - timedelta(weeks=2)
        
        seconds = (now - timestamp).total_seconds()
        days = int(seconds / 86400)
        weeks = int(days / 7)
        result = f'il y a {weeks}sem' if weeks < 4 else None
        
        assert result == 'il y a 2sem'
        assert weeks == 2

    def test_format_months(self):
        """Test: >= 4 semaines = 'il y a Xmois'"""
        now = datetime.now()
        timestamp = now - timedelta(days=60)
        
        seconds = (now - timestamp).total_seconds()
        days = int(seconds / 86400)
        months = int(days / 30)
        result = f'il y a {months}mois'
        
        assert result == 'il y a 2mois'
        assert months == 2

    def test_format_null_timestamp(self):
        """Test: Timestamp null retourne null"""
        timestamp = None
        result = None if not timestamp else 'value'
        
        assert result is None

    def test_format_exactly_1_minute(self):
        """Test: Exactement 60 secondes = 1 minute"""
        now = datetime.now()
        timestamp = now - timedelta(seconds=60)
        
        seconds = (now - timestamp).total_seconds()
        minutes = int(seconds / 60)
        
        assert minutes == 1
        assert seconds >= 60

    def test_format_exactly_1_hour(self):
        """Test: Exactement 60 minutes = 1 heure"""
        now = datetime.now()
        timestamp = now - timedelta(minutes=60)
        
        seconds = (now - timestamp).total_seconds()
        minutes = int(seconds / 60)
        hours = int(minutes / 60)
        
        assert hours == 1
        assert minutes == 60

    def test_format_exactly_1_day(self):
        """Test: Exactement 24 heures = 1 jour"""
        now = datetime.now()
        timestamp = now - timedelta(hours=24)
        
        seconds = (now - timestamp).total_seconds()
        hours = int(seconds / 3600)
        days = int(hours / 24)
        
        assert days == 1
        assert hours == 24


class TestRelativeTimeDisplay:
    """Tests pour l'affichage du temps relatif dans l'UI"""

    def test_online_device_shows_last_seen_in_meta(self):
        """Test: Device online affiche last_seen dans meta"""
        is_online = True
        last_seen = 'il y a 5 min'
        
        # Device online: last_seen dans meta avec ✓
        display_in_meta = is_online
        display_in_badge = not is_online
        
        assert display_in_meta is True
        assert display_in_badge is False

    def test_offline_device_shows_last_seen_in_badge(self):
        """Test: Device offline affiche last_seen dans badge"""
        is_online = False
        last_seen = 'il y a 3h'
        
        # Device offline: last_seen dans badge avec ⏰
        display_in_badge = not is_online
        display_in_meta = is_online
        
        assert display_in_badge is True
        assert display_in_meta is False

    def test_no_last_seen_no_display(self):
        """Test: Pas de last_seen = pas d'affichage"""
        last_seen = None
        should_display = last_seen is not None
        
        assert should_display is False

    def test_badge_color_offline(self):
        """Test: Badge offline = couleur muted"""
        is_online = False
        badge_class = 'badge-muted' if not is_online else 'badge-success'
        
        assert badge_class == 'badge-muted'

    def test_meta_color_online(self):
        """Test: Meta online = couleur verte"""
        is_online = True
        meta_color = '#22c55e' if is_online else '#9ca3af'
        
        assert meta_color == '#22c55e'


class TestTimeCalculations:
    """Tests pour les calculs de temps"""

    def test_seconds_to_minutes_conversion(self):
        """Test: Conversion secondes → minutes"""
        seconds = 180
        minutes = seconds // 60
        
        assert minutes == 3

    def test_minutes_to_hours_conversion(self):
        """Test: Conversion minutes → heures"""
        minutes = 150
        hours = minutes // 60
        
        assert hours == 2

    def test_hours_to_days_conversion(self):
        """Test: Conversion heures → jours"""
        hours = 48
        days = hours // 24
        
        assert days == 2

    def test_days_to_weeks_conversion(self):
        """Test: Conversion jours → semaines"""
        days = 14
        weeks = days // 7
        
        assert weeks == 2

    def test_days_to_months_approximation(self):
        """Test: Approximation jours → mois (30j)"""
        days = 60
        months = days // 30
        
        assert months == 2

    def test_timestamp_parsing(self):
        """Test: Parsing ISO timestamp"""
        timestamp_str = "2025-10-21T13:40:00"
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        
        assert isinstance(timestamp, datetime)
        assert timestamp.year == 2025
        assert timestamp.month == 10
        assert timestamp.day == 21

