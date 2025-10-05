from django.db import transaction as db_transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from .models import Invoice, InvoiceItem, Item, Transaction, Inventory


class InvoiceService:
    """
    A service class that encapsulates all business logic related to Invoices.
    """
    @staticmethod
    @db_transaction.atomic
    def create_invoice(customer_data: dict, items_data: list) -> Invoice:
        """
        Creates a new Invoice, its line items, allocates stock, 
        and creates the initial 'Sale' transaction.
        """
        # Create the main invoice object
        invoice = Invoice.objects.create(**customer_data)

        for item_data in items_data:
            # Create the invoice line item
            invoice_item = InvoiceItem.objects.create(
                invoice=invoice,
                item=item_data['item'],
                quantity=item_data['quantity']
            )
            
            # Allocate stock for the item
            inventory = invoice_item.item.inventory
            if inventory.quantity_available < invoice_item.quantity:
                raise ValidationError(f"Not enough stock available for {inventory.item.name}. Available: {inventory.quantity_available}")
            
            inventory.quantity_allocated = F('quantity_allocated') + invoice_item.quantity
            inventory.save(update_fields=['quantity_allocated'])

        # Create the initial 'Sale' transaction
        Transaction.objects.create(
            invoice=invoice,
            transaction_type='sale',
            amount_cents=invoice.total_amount_cents,
            notes=f"Sale transaction for invoice {invoice.reference_number}"
        )

        return invoice

    @staticmethod
    @db_transaction.atomic
    def mark_as_paid(invoice: Invoice, notes: str = "Payment received") -> Invoice:
        """
        Marks an invoice as paid, creates the 'Payment' transaction,
        and finalizes the stock deduction.
        """
        # Finalize stock deduction
        for item in invoice.invoiceitem_set.all():
            inventory = item.item.inventory
            inventory.quantity_on_hand = F('quantity_on_hand') - item.quantity
            inventory.quantity_allocated = F('quantity_allocated') - item.quantity
            inventory.save(update_fields=['quantity_on_hand', 'quantity_allocated'])

        # Update invoice status
        invoice.status = 'paid'
        invoice.save(update_fields=['status'])

        # Create the 'Payment' transaction
        Transaction.objects.create(
            invoice=invoice,
            transaction_type='payment',
            amount_cents=invoice.total_amount_cents,
            notes=notes
        )

        return invoice

    @staticmethod
    @db_transaction.atomic
    def cancel_invoice(invoice: Invoice) -> Invoice:
        """
        Cancels a pending invoice and releases the allocated stock.
        """
        if invoice.status == 'paid':
            raise ValidationError("Cannot cancel a paid invoice.")
        if invoice.status == 'cancelled':
            return invoice # Already cancelled

        # Release the allocated stock
        for item in invoice.invoiceitem_set.all():
            inventory = item.item.inventory
            inventory.quantity_allocated = F('quantity_allocated') - item.quantity
            inventory.save(update_fields=['quantity_allocated'])
        
        invoice.status = 'cancelled'
        invoice.save(update_fields=['status'])
        return invoice
