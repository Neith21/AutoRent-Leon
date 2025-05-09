from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from simple_history import register

# Añadir HistoricalRecords al modelo User mediante monkey patching
User.history = HistoricalRecords()
register(User)