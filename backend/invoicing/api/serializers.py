from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from ..models import Item, Inventory, Invoice, InvoiceItem, Transaction
from ..services import InvoiceService



class ItemSerializer(serializers.ModelSerializer):
    unit_price_cash = serializers.FloatField(read_only=True)
    quantity_available = serializers.IntegerField(source='inventory.quantity_available', read_only=True)
    
    class Meta:
        model = Item
        fields = [
            'id', 
            'name', 
            'description', 
            'unit_price_cents', 
            'unit_price_cash', 
            'quantity_available'
        ]

class InventorySerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    
    class Meta:
        model = Inventory
        fields = ['id', 'item', 'item_name', 'stock_quantity']

class InvoiceItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    unit_price_cents = serializers.IntegerField(source='item.unit_price_cents', read_only=True)
    unit_price_cash = serializers.FloatField(source='item.unit_price_cash', read_only=True)
    total_price_cents = serializers.IntegerField(read_only=True)
    total_price_cash = serializers.FloatField(read_only=True)
    
    class Meta:
        model = InvoiceItem
        fields = ['id', 'item', 'item_name', 'quantity', 'unit_price_cents', 
                  'unit_price_cash', 'total_price_cents', 'total_price_cash']

class InvoiceItemCreateSerializer(serializers.Serializer):
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all())
    quantity = serializers.IntegerField(min_value=1)

class InvoiceSerializer(serializers.ModelSerializer):
    invoice_items = InvoiceItemSerializer(source='invoiceitem_set', many=True, read_only=True)
    total_amount_cents = serializers.IntegerField(read_only=True)
    total_amount_cash = serializers.FloatField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Invoice
        fields = ['id', 'reference_number', 'customer_name', 'customer_email', 
                  'customer_address', 'customer_phone', 'invoice_date', 'due_date',
                  'status', 'invoice_items', 'total_amount_cents', 'total_amount_cash',
                  'is_overdue']
        read_only_fields = ['reference_number', 'invoice_date', 'status']


class InvoiceCreateSerializer(serializers.ModelSerializer):
    items = InvoiceItemCreateSerializer(many=True, write_only=True)
    
    class Meta:
        model = Invoice
        fields = ['customer_name', 'customer_email', 'customer_address', 
                  'customer_phone', 'due_date', 'items']
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Invoice must have at least one item.")
        return value
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        try:
            # Delegate the entire creation operation to the service class
            return InvoiceService.create_invoice(customer_data=validated_data, items_data=items_data)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.error_list)


class InvoiceUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an invoice. Only allows updating customer details
    and due date, and only for invoices that are still pending.
    """
    class Meta:
        model = Invoice
        fields = [
            'customer_name', 
            'customer_email', 
            'customer_address', 
            'customer_phone', 
            'due_date'
        ]

    def validate(self, data):
        """
        Check that the invoice is in 'pending' status before allowing updates.
        """
        if self.instance and self.instance.status != 'pending':
            raise serializers.ValidationError("Updates are only allowed for invoices with 'pending' status.")
        return data


class InvoicePaymentSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True, default="Payment received")
    
    def validate(self, data):
        invoice = self.context['invoice']
        
        if invoice.status != 'pending':
            raise serializers.ValidationError("Only pending invoices can be marked as paid.")
        
        return data
    
    def save(self):
        invoice = self.context['invoice']
        notes = self.validated_data.get('notes', "Payment received")
        
        # Delegate the payment operation to the service class
        return InvoiceService.mark_as_paid(invoice=invoice, notes=notes)


class InvoiceCancelSerializer(serializers.Serializer):
    """
    Serializer for the cancel invoice action. It does not require any input fields,
    but handles the validation and service call for the cancellation.
    """
    def validate(self, data):
        invoice = self.context['invoice']
        if invoice.status == 'paid':
            raise serializers.ValidationError("Cannot cancel a paid invoice.")
        if invoice.status == 'cancelled':
            raise serializers.ValidationError("Invoice is already cancelled.")
        return data

    def save(self):
        invoice = self.context['invoice']
        return InvoiceService.cancel_invoice(invoice=invoice)


class TransactionSerializer(serializers.ModelSerializer):
    invoice_reference = serializers.CharField(source='invoice.reference_number', read_only=True)
    amount_cash = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'invoice', 'invoice_reference', 'transaction_type', 
                  'amount_cents', 'amount_cash', 'notes', 'timestamp']
        read_only_fields = ['timestamp']

class InvoiceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing invoices"""
    total_amount = serializers.FloatField(source='total_amount_cash', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    items_count = serializers.SerializerMethodField()
    payment_date = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'reference_number', 'customer_name', 'customer_email',
            'invoice_date', 'due_date', 'status', 'total_amount',
            'is_overdue', 'items_count', 'payment_date'
        ]
        read_only_fields = ['id', 'reference_number', 'invoice_date', 'total_amount', 'is_overdue', 'payment_date']

    def get_items_count(self, obj):
        # This is efficient thanks to prefetch_related('invoiceitem_set') in the view
        return len(obj.invoiceitem_set.all())

    def get_payment_date(self, obj):
        if obj.status == 'paid':
            # This is efficient thanks to prefetch_related('transactions') in the view
            payment_transaction = next((t for t in reversed(obj.transactions.all()) if t.transaction_type == 'payment'), None)
            if payment_transaction:
                return payment_transaction.timestamp
        return None

class InvoiceDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for invoice retrieval"""
    items = InvoiceItemSerializer(many=True, read_only=True, source='invoiceitem_set')
    transactions = TransactionSerializer(many=True, read_only=True)
    total_amount = serializers.FloatField(source='total_amount_cash', read_only=True)
    total_amount_cents = serializers.IntegerField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'reference_number', 'customer_name', 'customer_email',
            'customer_address', 'customer_phone', 'invoice_date', 'due_date',
            'status', 'total_amount', 'total_amount_cents', 'is_overdue',
            'items', 'transactions'
        ]
        read_only_fields = [
            'id', 'reference_number', 'invoice_date', 'total_amount', 
            'total_amount_cents', 'is_overdue', 'items', 'transactions'
        ]