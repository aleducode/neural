"""Membership views for API v1."""

import hashlib
import random
import string

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from neural.api.serializers.membership import (
    NeuralPlanSerializer,
    UserMembershipSerializer,
)
from neural.users.models import NeuralPlan, UserMembership, UserPaymentReference


class MembershipView(APIView):
    """Get current membership and available plans."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Current membership
        current_membership = None
        active = (
            UserMembership.objects.filter(user=user, is_active=True)
            .select_related("plan")
            .first()
        )
        if active:
            current_membership = UserMembershipSerializer(active).data

        # Available plans
        plans = NeuralPlan.objects.all().order_by("duration")

        return Response(
            {
                "current_membership": current_membership,
                "available_plans": NeuralPlanSerializer(plans, many=True).data,
            }
        )


class CreatePaymentView(APIView):
    """Create a payment reference for BOLD."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get("plan_id")

        if not plan_id:
            return Response(
                {"error": "plan_id es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            plan = NeuralPlan.objects.get(id=plan_id)
        except NeuralPlan.DoesNotExist:
            return Response(
                {"error": "Plan no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Generate unique reference
        reference = "".join(random.choices(string.ascii_letters + string.digits, k=16))

        # Create payment reference
        UserPaymentReference.objects.create(
            user=request.user,
            reference=reference,
            amount=plan.price,
            plan=plan,
        )

        # Generate BOLD integrity signature
        amount = int(plan.price)
        secret_key = settings.BOLD_SECRET
        data_to_hash = f"{reference}{amount}COP{secret_key}"
        integrity_signature = hashlib.sha256(data_to_hash.encode()).hexdigest()

        return Response(
            {
                "reference": reference,
                "amount": amount,
                "currency": "COP",
                "integrity_signature": integrity_signature,
                "bold_public_key": settings.BOLD_KEY,
                "plan": NeuralPlanSerializer(plan).data,
            }
        )


class VerifyPaymentView(APIView):
    """Verify a payment and activate membership."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")
        tx_status = request.data.get("tx_status")

        if not order_id:
            return Response(
                {"error": "order_id es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment_ref = UserPaymentReference.objects.get(
                reference=order_id, user=request.user
            )
        except UserPaymentReference.DoesNotExist:
            return Response(
                {"error": "Referencia de pago no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if payment_ref.is_paid:
            return Response(
                {
                    "success": True,
                    "message": "Este pago ya fue procesado",
                }
            )

        if tx_status == "approved":
            payment_ref.apply_membership()

            # Get updated membership
            membership = (
                UserMembership.objects.filter(user=request.user, is_active=True)
                .select_related("plan")
                .first()
            )

            return Response(
                {
                    "success": True,
                    "message": "Membresía activada exitosamente",
                    "membership": {
                        "plan_name": membership.plan.name
                        if membership and membership.plan
                        else None,
                        "expiration_date": membership.expiration_date.isoformat()
                        if membership
                        else None,
                        "days_left": membership.days_left if membership else 0,
                    },
                }
            )
        else:
            return Response(
                {
                    "success": False,
                    "message": "El pago no fue aprobado",
                }
            )


class PaymentWebhookView(APIView):
    """Webhook for BOLD payment notifications."""

    permission_classes = [AllowAny]

    def post(self, request):
        # Get payment data from BOLD
        data = request.data
        order_id = data.get("order_id") or data.get("reference")
        tx_status = data.get("status") or data.get("tx_status")

        if not order_id:
            return Response(
                {"error": "order_id not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment_ref = UserPaymentReference.objects.get(reference=order_id)
        except UserPaymentReference.DoesNotExist:
            return Response(
                {"error": "Payment reference not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Store webhook data
        payment_ref.data = data
        payment_ref.save()

        if tx_status in ["approved", "APPROVED"]:
            payment_ref.apply_membership()

        return Response({"success": True})

    def get(self, request):
        # Handle GET redirect from BOLD
        order_id = request.query_params.get("bold-order-id")
        tx_status = request.query_params.get("bold-tx-status")

        if order_id and tx_status in ["approved", "APPROVED"]:
            try:
                payment_ref = UserPaymentReference.objects.get(reference=order_id)
                if not payment_ref.is_paid:
                    payment_ref.apply_membership()
            except UserPaymentReference.DoesNotExist:
                pass

        return Response({"success": True})
