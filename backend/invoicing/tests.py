from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .services import InvoiceService
from .models import Invoice, Item, Inventory, Transaction


class InvoiceAPITests(APITestCase):
    """
    Test suite for the Invoice API endpoints.
    """

    def setUp(self):
        """
        Set up the necessary objects for the tests.
        This method is run before each test.
        """
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        # Get JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Create some items and inventory
        self.item1 = Item.objects.create(name="Test Item 1", description="A test item", unit_price_cents=1000)
        self.inventory1 = Inventory.objects.create(item=self.item1, quantity_on_hand=100)

        self.item2 = Item.objects.create(name="Test Item 2", description="Another test item", unit_price_cents=500)
        self.inventory2 = Inventory.objects.create(item=self.item2, quantity_on_hand=50)

    def test_create_invoice(self):
        """
        Ensure we can create a new invoice.
        """
        url = '/api/invoices/'
        data = {
            "customer_name": "Test Customer",
            "due_date": "2025-12-31",
            "items": [
                {"item": self.item1.id, "quantity": 2},
                {"item": self.item2.id, "quantity": 5}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        # 1. Check the response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer_name'], "Test Customer")

        # 2. Check the database state
        self.assertEqual(Invoice.objects.count(), 1)
        invoice = Invoice.objects.first()
        self.assertEqual(invoice.invoiceitem_set.count(), 2)
        self.assertEqual(invoice.status, 'pending')

        # 3. Check calculated total (2 * 1000) + (5 * 500) = 2000 + 2500 = 4500 cents
        self.assertEqual(invoice.total_amount_cents, 4500)

        # 4. Check that a 'Sale' transaction was created
        self.assertEqual(Transaction.objects.count(), 1)
        sale_transaction = Transaction.objects.first()
        self.assertEqual(sale_transaction.transaction_type, 'sale')
        self.assertEqual(sale_transaction.amount_cents, 4500)

        # 5. Check that stock was allocated
        self.inventory1.refresh_from_db()
        self.assertEqual(self.inventory1.quantity_allocated, 2)
        self.assertEqual(self.inventory1.quantity_available, 98) # 100 - 2

    def test_pay_invoice(self):
        """
        Ensure we can pay a pending invoice.
        """
        # First, create an invoice to pay
        invoice = InvoiceService.create_invoice(
            customer_data={"customer_name": "To Be Paid Customer", "due_date": "2025-12-31"},
            items_data=[{"item": self.item1, "quantity": 10}]
        )
        self.assertEqual(invoice.status, 'pending')
        self.assertEqual(Transaction.objects.count(), 1) # Only the sale transaction exists

        # Now, pay the invoice
        url = f'/api/invoices/{invoice.id}/pay/'
        response = self.client.post(url, {}, format='json')

        # 1. Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'paid')

        # 2. Check the database state
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, 'paid')

        # 3. Check that a 'Payment' transaction was created
        self.assertEqual(Transaction.objects.count(), 2)
        payment_transaction = Transaction.objects.get(transaction_type='payment')
        self.assertEqual(payment_transaction.amount_cents, invoice.total_amount_cents)

        # 4. Check that stock was finalized
        self.inventory1.refresh_from_db()
        self.assertEqual(self.inventory1.quantity_on_hand, 90) # 100 - 10
        self.assertEqual(self.inventory1.quantity_allocated, 0) # 10 allocated - 10 sold
        self.assertEqual(self.inventory1.quantity_available, 90)

    def test_pay_paid_invoice_fails(self):
        """
        Ensure we cannot pay an invoice that is already paid.
        """
        # Create and pay an invoice
        invoice = InvoiceService.create_invoice(
            customer_data={"customer_name": "Already Paid Customer", "due_date": "2025-12-31"},
            items_data=[{"item": self.item1, "quantity": 1}]
        )
        InvoiceService.mark_as_paid(invoice=invoice)
        self.assertEqual(invoice.status, 'paid')

        # Attempt to pay it again
        url = f'/api/invoices/{invoice.id}/pay/'
        response = self.client.post(url, {}, format='json')

        # Check that the request was rejected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_pending_invoice(self):
        """
        Ensure we can cancel a pending invoice and stock is released.
        """
        invoice = InvoiceService.create_invoice(
            customer_data={"customer_name": "To Be Cancelled", "due_date": "2025-12-31"},
            items_data=[{"item": self.item1, "quantity": 5}]
        )
        self.inventory1.refresh_from_db()
        self.assertEqual(self.inventory1.quantity_allocated, 5)

        url = f'/api/invoices/{invoice.id}/cancel/'
        response = self.client.post(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, 'cancelled')

        # Check that allocated stock was released
        self.inventory1.refresh_from_db()
        self.assertEqual(self.inventory1.quantity_allocated, 0)
        self.assertEqual(self.inventory1.quantity_on_hand, 100) # On-hand stock is not affected

    def test_cancel_paid_invoice_fails(self):
        """
        Ensure we cannot cancel an already paid invoice.
        """
        invoice = InvoiceService.create_invoice(
            customer_data={"customer_name": "Cannot Cancel Paid", "due_date": "2025-12-31"},
            items_data=[{"item": self.item1, "quantity": 1}]
        )
        InvoiceService.mark_as_paid(invoice=invoice)

        url = f'/api/invoices/{invoice.id}/cancel/'
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_pending_invoice(self):
        """
        Ensure we can update the customer details of a pending invoice.
        """
        invoice = InvoiceService.create_invoice(
            customer_data={"customer_name": "Original Name", "due_date": "2025-12-31"},
            items_data=[{"item": self.item1, "quantity": 1}]
        )
        url = f'/api/invoices/{invoice.id}/'
        update_data = {"customer_name": "Updated Name"}
        response = self.client.patch(url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invoice.refresh_from_db()
        self.assertEqual(invoice.customer_name, "Updated Name")

    def test_create_invoice_insufficient_stock_fails(self):
        """
        Ensure creating an invoice fails if stock is insufficient.
        """
        url = '/api/invoices/'
        data = {
            "customer_name": "Test Customer",
            "due_date": "2025-12-31",
            "items": [
                {"item": self.item1.id, "quantity": 200} # We only have 100 on hand
            ]
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure no invoice or transaction was created due to the atomic transaction
        self.assertEqual(Invoice.objects.count(), 0)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_unauthenticated_access_fails(self):
        """
        Ensure unauthenticated users cannot access the API.
        """
        self.client.credentials() # Clear authentication
        url = '/api/invoices/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)