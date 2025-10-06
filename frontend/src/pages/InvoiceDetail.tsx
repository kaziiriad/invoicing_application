import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Layout from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { invoiceApi } from '@/lib/api';
import { ArrowLeft, CreditCard, XCircle } from 'lucide-react';
import { toast } from 'sonner';

const InvoiceDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showPayDialog, setShowPayDialog] = useState(false);
  const [showCancelDialog, setShowCancelDialog] = useState(false);

  const { data: invoice, isLoading } = useQuery({
    queryKey: ['invoice', id],
    queryFn: () => invoiceApi.get(Number(id)),
    enabled: !!id,
  });

  const payMutation = useMutation({
    mutationFn: () => invoiceApi.pay(Number(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoice', id] });
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      toast.success('Invoice marked as paid');
      setShowPayDialog(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to mark invoice as paid');
    },
  });

  const cancelMutation = useMutation({
    mutationFn: () => invoiceApi.cancel(Number(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoice', id] });
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      toast.success('Invoice cancelled');
      setShowCancelDialog(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to cancel invoice');
    },
  });

  const getStatusBadge = (status: string) => {
    const variants = {
      pending: 'bg-warning/10 text-warning',
      paid: 'bg-success/10 text-success',
      cancelled: 'bg-destructive/10 text-destructive',
    };
    return variants[status as keyof typeof variants] || variants.pending;
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="flex justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
        </div>
      </Layout>
    );
  }

  if (!invoice) {
    return (
      <Layout>
        <div className="py-12 text-center">
          <p className="text-muted-foreground">Invoice not found</p>
          <Link to="/invoices">
            <Button variant="ghost" className="mt-4">Back to Invoices</Button>
          </Link>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => navigate('/invoices')}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-foreground">{invoice.reference_number}</h1>
              <p className="mt-1 text-muted-foreground">Invoice Details</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {invoice.status === 'pending' && (
              <>
                <Button
                  variant="outline"
                  onClick={() => setShowCancelDialog(true)}
                  className="text-destructive hover:bg-destructive/10"
                >
                  <XCircle className="mr-2 h-4 w-4" />
                  Cancel
                </Button>
                <Button
                  onClick={() => setShowPayDialog(true)}
                  className="bg-success hover:bg-success/90"
                >
                  <CreditCard className="mr-2 h-4 w-4" />
                  Mark as Paid
                </Button>
              </>
            )}
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-6">
            <Card className="shadow-soft">
              <CardHeader>
                <CardTitle>Customer Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm text-muted-foreground">Name</p>
                  <p className="font-medium">{invoice.customer_name}</p>
                </div>
                {invoice.customer_email && (
                  <div>
                    <p className="text-sm text-muted-foreground">Email</p>
                    <p className="font-medium">{invoice.customer_email}</p>
                  </div>
                )}
                {invoice.customer_phone && (
                  <div>
                    <p className="text-sm text-muted-foreground">Phone</p>
                    <p className="font-medium">{invoice.customer_phone}</p>
                  </div>
                )}
                {invoice.customer_address && (
                  <div>
                    <p className="text-sm text-muted-foreground">Address</p>
                    <p className="font-medium whitespace-pre-wrap">{invoice.customer_address}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="shadow-soft">
              <CardHeader>
                <CardTitle>Line Items</CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Item</TableHead>
                      <TableHead className="text-right">Quantity</TableHead>
                      <TableHead className="text-right">Unit Price</TableHead>
                      <TableHead className="text-right">Total</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {invoice.items?.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell className="font-medium">{item.item_name}</TableCell>
                        <TableCell className="text-right">{item.quantity}</TableCell>
                        <TableCell className="text-right">{formatCurrency(item.unit_price_cash)}</TableCell>
                        <TableCell className="text-right font-semibold">
                          {formatCurrency(item.total_price_cash)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                <div className="mt-4 flex justify-end border-t pt-4">
                  <div className="space-y-2">
                    <div className="flex justify-between gap-12">
                      <span className="text-muted-foreground">Subtotal</span>
                      <span className="font-semibold">{formatCurrency(invoice.total_amount)}</span>
                    </div>
                    <div className="flex justify-between gap-12 text-lg">
                      <span className="font-semibold">Total</span>
                      <span className="font-bold text-primary">{formatCurrency(invoice.total_amount)}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {invoice.transactions && invoice.transactions.length > 0 && (
              <Card className="shadow-soft">
                <CardHeader>
                  <CardTitle>Transaction History</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {invoice.transactions.map((transaction) => (
                      <div key={transaction.id} className="flex items-center justify-between rounded-lg border p-4">
                        <div>
                          <p className="font-medium capitalize">{transaction.transaction_type}</p>
                          <p className="text-sm text-muted-foreground">{transaction.notes}</p>
                          <p className="text-sm text-muted-foreground">
                            {new Date(transaction.timestamp).toLocaleString()}
                          </p>
                        </div>
                        <p className="font-semibold">{formatCurrency(transaction.amount_cash)}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          <div className="space-y-6">
            <Card className="shadow-soft">
              <CardHeader>
                <CardTitle>Invoice Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground">Status</p>
                  <div className="mt-1 flex items-center gap-2">
                    <Badge className={getStatusBadge(invoice.status)}>
                      {invoice.status}
                    </Badge>
                    {invoice.is_overdue && (
                      <Badge className="bg-destructive/10 text-destructive">Overdue</Badge>
                    )}
                  </div>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Invoice Date</p>
                  <p className="font-medium">{new Date(invoice.invoice_date).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Due Date</p>
                  <p className="font-medium">{new Date(invoice.due_date).toLocaleDateString()}</p>
                </div>
                <div className="border-t pt-4">
                  <p className="text-sm text-muted-foreground">Total Amount</p>
                  <p className="text-2xl font-bold text-primary">{formatCurrency(invoice.total_amount)}</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      <AlertDialog open={showPayDialog} onOpenChange={setShowPayDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Mark Invoice as Paid</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to mark this invoice as paid? This will create a payment transaction
              and update the invoice status.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => payMutation.mutate()}
              className="bg-success hover:bg-success/90"
            >
              Confirm Payment
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={showCancelDialog} onOpenChange={setShowCancelDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Cancel Invoice</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to cancel this invoice? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Go Back</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => cancelMutation.mutate()}
              className="bg-destructive hover:bg-destructive/90"
            >
              Cancel Invoice
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Layout>
  );
};

export default InvoiceDetail;
