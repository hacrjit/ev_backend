from decimal import Decimal
from django.db import transaction
from .models import Wallet, Transaction
import razorpay
from django.conf import settings
import hmac
import hashlib

def get_or_create_wallet(user):
    wallet, _ = Wallet.objects.get_or_create(user=user)
    return wallet

@transaction.atomic
def recharge_wallet(user, amount, description="Wallet Recharge"):
    wallet = Wallet.objects.select_for_update().get(user=user)
    wallet.balance += Decimal(amount)
    wallet.save()
    txn = Transaction.objects.create(wallet=wallet, txn_type="credit", amount=amount, description=description)
    return txn

@transaction.atomic
def debit_wallet(user, amount, description="Service Usage"):
    wallet = Wallet.objects.select_for_update().get(user=user)
    if wallet.balance < Decimal(amount):
        raise ValueError("Insufficient balance")
    wallet.balance -= Decimal(amount)
    wallet.save()
    txn = Transaction.objects.create(wallet=wallet, txn_type="debit", amount=amount, description=description)
    return txn




razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_razorpay_order(amount):
    amount_paise = int(float(amount) * 100)  # Razorpay takes amount in paisa
    order = razorpay_client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": 1
    })
    return order

@transaction.atomic
def verify_and_recharge(user, razorpay_payment_id, razorpay_order_id, razorpay_signature):
    body = f"{razorpay_order_id}|{razorpay_payment_id}"
    expected_signature = hmac.new(
        key=bytes(settings.RAZORPAY_KEY_SECRET, 'utf-8'),
        msg=bytes(body, 'utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

    if expected_signature != razorpay_signature:
        raise ValueError("Invalid payment signature")

    payment_info = razorpay_client.payment.fetch(razorpay_payment_id)
    amount = Decimal(payment_info['amount']) / 100  # Convert paisa to rupees

    wallet, _ = Wallet.objects.get_or_create(user=user)
    wallet.balance += amount
    wallet.save()

    txn = Transaction.objects.create(
        wallet=wallet,
        txn_type='credit',
        amount=amount,
        description="Razorpay Recharge"
    )
    return txn