from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ErrorLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_error = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    error_message = models.TextField()
    stack_trace = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.date_error} | {self.user} | {self.action}"
