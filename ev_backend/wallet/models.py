import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(default=0.0, max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.user.email} - ₹{self.balance}"

class Transaction(models.Model):
    TXN_TYPE_CHOICES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    txn_type = models.CharField(choices=TXN_TYPE_CHOICES, max_length=10)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.txn_type.upper()} ₹{self.amount} - {self.wallet.user.email}"