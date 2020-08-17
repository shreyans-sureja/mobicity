from django.db import models
from api.user.models import CustomUser

class PaymentCards(models.Model):
    number = models.CharField(max_length=16)
    expiry = models.CharField(max_length=10)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.number