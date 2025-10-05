from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import Invoice
from .serializers import (
    InvoiceCreateSerializer,
    InvoiceDetailSerializer,
    InvoiceListSerializer,
    InvoicePaymentSerializer,
    InvoiceUpdateSerializer,
    InvoiceCancelSerializer,
)

class InvoiceViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for listing, creating, retrieving, and paying invoices.
    """
    queryset = Invoice.objects.all().order_by('-invoice_date')

    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        """
        if self.action == 'list':
            return InvoiceListSerializer
        if self.action == 'create':
            return InvoiceCreateSerializer
        if self.action in ['update', 'partial_update']:
            return InvoiceUpdateSerializer
        return InvoiceDetailSerializer

    @swagger_auto_schema(
        operation_summary="Create a new Invoice",
        request_body=InvoiceCreateSerializer,
        responses={
            201: openapi.Response(
                description="Invoice created successfully.",
                schema=InvoiceDetailSerializer
            ),
            400: "Bad Request (e.g., invalid data)."
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Mark an Invoice as Paid",
        operation_description="Updates the status of a PENDING invoice to PAID. This is an idempotent action.",
        request_body=InvoicePaymentSerializer,
        responses={
            200: openapi.Response(
                description="Payment successful. Returns the updated invoice details.",
                schema=InvoiceDetailSerializer
            ),
            400: "Bad Request (e.g., invoice is not in a pending state).",
        }
    )
    @action(detail=True, methods=['post'], url_path='pay')
    def mark_as_paid(self, request, pk=None):
        """
        A custom action to mark an invoice as paid.
        This creates the endpoint: POST /api/invoices/{id}/pay/
        """
        invoice = self.get_object()
        
        serializer = InvoicePaymentSerializer(
            context={'invoice': invoice},
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        
        paid_invoice = serializer.save()
        
        response_serializer = InvoiceDetailSerializer(paid_invoice)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Cancel a Pending Invoice",
        operation_description="Updates the status of a PENDING invoice to CANCELLED and releases allocated stock.",
        request_body=InvoiceCancelSerializer,
        responses={
            200: openapi.Response(
                description="Cancellation successful. Returns the updated invoice details.",
                schema=InvoiceDetailSerializer
            ),
            400: "Bad Request (e.g., invoice is already paid or cancelled).",
        }
    )
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_invoice(self, request, pk=None):
        """
        A custom action to cancel a pending invoice.
        This creates the endpoint: POST /api/invoices/{id}/cancel/
        """
        invoice = self.get_object()
        
        serializer = InvoiceCancelSerializer(
            context={'invoice': invoice},
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        
        cancelled_invoice = serializer.save()
        
        response_serializer = InvoiceDetailSerializer(cancelled_invoice)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
