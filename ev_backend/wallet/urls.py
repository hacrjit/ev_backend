from django.urls import path
from .views import WalletBalanceView, RechargeWalletView, DebitWalletView, TransactionHistoryView, CreateRazorpayOrder, VerifyRazorpayPayment, WalletRechargePageView

urlpatterns = [
    path('', WalletBalanceView.as_view(), name='wallet-balance'),
    path('recharge/', RechargeWalletView.as_view(), name='wallet-recharge'),
    path('debit/', DebitWalletView.as_view(), name='wallet-debit'),
    path('transactions/', TransactionHistoryView.as_view(), name='wallet-transactions'),

    path('create-payment/', CreateRazorpayOrder.as_view(), name='create-payment'),
    path('verify-payment/', VerifyRazorpayPayment.as_view(), name='verify-payment'),

    path('recharge-page/', WalletRechargePageView.as_view(), name='wallet-recharge-page'),


]
