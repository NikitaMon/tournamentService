from django.db import models
from tournaments.models import Registration
from django.utils.translation import gettext as _

class Payment(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name='payments')
    payment_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='RUB')
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"Payment {self.payment_id} - {self.amount} {self.currency}"

    class Meta:
        ordering = ['-created_at']