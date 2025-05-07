from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .models import Transaction
from .serializers import WalletSerializer, TransactionSerializer
from .services import get_or_create_wallet, recharge_wallet, debit_wallet, create_razorpay_order, verify_and_recharge
from django.conf import settings

class WalletBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet = get_or_create_wallet(request.user)
        return Response(WalletSerializer(wallet).data)

class RechargeWalletView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            amount = float(request.data.get("amount"))
            txn = recharge_wallet(request.user, amount)
            return Response(TransactionSerializer(txn).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class DebitWalletView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            amount = float(request.data.get("amount"))
            txn = debit_wallet(request.user, amount)
            return Response(TransactionSerializer(txn).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class TransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet = get_or_create_wallet(request.user)
        txns = wallet.transactions.all().order_by('-timestamp')
        return Response(TransactionSerializer(txns, many=True).data)




class CreateRazorpayOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        if not amount or float(amount) <= 0:
            return Response({"error": "Invalid amount"}, status=400)
        
        try:
            order = create_razorpay_order(amount)
            return Response({
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "amount": order['amount'],
                "currency": order['currency'],
                "order_id": order['id']
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class VerifyRazorpayPayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            txn = verify_and_recharge(
                user=request.user,
                razorpay_payment_id=request.data['razorpay_payment_id'],
                razorpay_order_id=request.data['razorpay_order_id'],
                razorpay_signature=request.data['razorpay_signature']
            )
            return Response({"message": "Recharge successful", "transaction_id": str(txn.id)})
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        

class WalletRechargePageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return render(request, 'recharge_wallet.html')