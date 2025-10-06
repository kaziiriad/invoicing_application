from django.db import models
from django.utils import timezone

# Create your models here.

class Item(models.Model):
    """Represents a product or service that can be invoiced."""
    name = models.CharField(max_length=255)
    description = models.TextField()
    unit_price_cents = models.PositiveIntegerField()

    class Meta:
        ordering = ['name']

    @property
    def unit_price_cash(self) -> float:
        if self.unit_price_cents is None:
            return 0.0
        return self.unit_price_cents / 100

    @unit_price_cash.setter
    def unit_price_cash(self, cash_value: float):
        self.unit_price_cents = int(cash_value * 100)

    def __str__(self):
        return self.name


class Inventory(models.Model):
    """Represents the stock level for a given Item."""
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name='inventory')
    quantity_on_hand = models.PositiveIntegerField(default=0)
    quantity_allocated = models.PositiveIntegerField(default=0)

    @property
    def quantity_available(self):
        return self.quantity_on_hand - self.quantity_allocated

    def __str__(self):
        return self.item.name


class Invoice(models.Model):
    """Represents an invoice, which is a collection of items sold to a customer."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    reference_number = models.CharField(max_length=50, unique=True, blank=True)
    customer_name = models.CharField(max_length=100, null=True, blank=True)
    customer_email = models.EmailField(null=True, blank=True)
    customer_address = models.TextField(null=True, blank=True)
    customer_phone = models.CharField(max_length=20, null=True, blank=True)
    # The ManyToManyField now uses the 'InvoiceItem' model as a through table
    items = models.ManyToManyField(Item, through='InvoiceItem', blank=True, related_name='invoices')
    invoice_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField(null=False, blank=False)

    def __str__(self):
        return self.reference_number or f"Invoice-{self.id}"

    def save(self, *args, **kwargs):

        is_new = self._state.adding

        if is_new:
            super().save(*args, **kwargs)

            date_obj = self.invoice_date
            year_short = str(date_obj.year)[-2:]
            day = str(date_obj.day).zfill(2)
            month = str(date_obj.month).zfill(2)

            ref_num = f"INVC-{year_short}{month}{day}-{str(self.id).zfill(4)}"

            Invoice.objects.filter(pk=self.pk).update(reference_number=ref_num)
            self.refresh_from_db()
        else:
            super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return self.due_date < timezone.now().date() and self.status == 'pending'

    @property
    def total_amount_cents(self):
        # Auto calculates the total from the related InvoiceItems
        return sum(item.total_price_cents for item in self.invoiceitem_set.all())

    @property
    def total_amount_cash(self) -> float:
        # Read-only property that returns the total in a cash format
        return self.total_amount_cents / 100


class InvoiceItem(models.Model):
    """
    This is the 'through' model for the Invoice-Item relationship.
    It allows us to specify the quantity of each item on an invoice.
    """
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = (('invoice', 'item'),) # Prevents adding the same item twice to one invoice

    @property
    def total_price_cents(self):
        return self.quantity * self.item.unit_price_cents

    @property
    def total_price_cash(self) -> float:
        return self.total_price_cents / 100

    def __str__(self):
        return f"{self.quantity} x {self.item.name} on {self.invoice}"


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('sale', 'Sale'),
        ('payment', 'Payment'),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount_cents = models.PositiveIntegerField()
    notes = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.amount_cents / 100} on {self.invoice}"

    @property
    def amount_cash(self) -> float:
        return self.amount_cents / 100
