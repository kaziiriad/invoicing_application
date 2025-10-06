import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { dashboardApi, invoiceApi } from '@/lib/api';
import { FileText, DollarSign, Clock, AlertCircle, Plus } from 'lucide-react';
import type { Invoice } from '@/types';

const Dashboard = () => {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: dashboardApi.getStats,
  });

  const { data: recentInvoices, isLoading: invoicesLoading } = useQuery({
    queryKey: ['recent-invoices'],
    queryFn: () => invoiceApi.list({ page: 1 }),
  });

  const getStatusBadge = (status: string) => {
    const variants = {
      pending: 'bg-warning/10 text-warning hover:bg-warning/20',
      paid: 'bg-success/10 text-success hover:bg-success/20',
      cancelled: 'bg-destructive/10 text-destructive hover:bg-destructive/20',
    };
    return variants[status as keyof typeof variants] || variants.pending;
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const statCards = [
    {
      title: 'Total Invoices',
      value: stats?.total_invoices || 0,
      icon: FileText,
      gradient: 'from-primary to-accent',
    },
    {
      title: 'Pending Invoices',
      value: stats?.pending_invoices || 0,
      icon: Clock,
      gradient: 'from-warning to-orange-400',
    },
    {
      title: 'Overdue',
      value: stats?.overdue_invoices || 0,
      icon: AlertCircle,
      gradient: 'from-destructive to-red-400',
    },
    {
      title: 'Total Revenue',
      value: formatCurrency(stats?.total_revenue || 0),
      icon: DollarSign,
      gradient: 'from-success to-green-400',
    },
  ];

  return (
    <Layout>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
            <p className="mt-2 text-muted-foreground">Overview of your invoicing system</p>
          </div>
          <Link to="/invoices/new">
            <Button className="bg-gradient-primary hover:opacity-90">
              <Plus className="mr-2 h-4 w-4" />
              New Invoice
            </Button>
          </Link>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {statCards.map((stat) => (
            <Card key={stat.title} className="shadow-soft">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-muted-foreground">{stat.title}</p>
                    <p className="text-3xl font-bold text-foreground">{stat.value}</p>
                  </div>
                  <div className={`flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${stat.gradient}`}>
                    <stat.icon className="h-6 w-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card className="shadow-soft">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Recent Invoices</CardTitle>
              <Link to="/invoices">
                <Button variant="ghost" size="sm">View All</Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            {invoicesLoading ? (
              <div className="flex justify-center py-8">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
              </div>
            ) : !recentInvoices?.results || recentInvoices.results.length === 0 ? (
              <div className="py-8 text-center text-muted-foreground">
                No invoices yet. Create your first invoice to get started.
              </div>
            ) : (
              <div className="space-y-3">
                {recentInvoices.results.slice(0, 5).map((invoice: Invoice) => (
                  <Link
                    key={invoice.id}
                    to={`/invoices/${invoice.id}`}
                    className="flex items-center justify-between rounded-lg border bg-card p-4 transition-colors hover:bg-secondary"
                  >
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-3">
                        <p className="font-semibold text-foreground">{invoice.reference_number}</p>
                        <Badge className={getStatusBadge(invoice.status)}>
                          {invoice.status}
                        </Badge>
                        {invoice.is_overdue && (
                          <Badge className="bg-destructive/10 text-destructive">Overdue</Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">{invoice.customer_name}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-foreground">{formatCurrency(invoice.total_amount)}</p>
                      <p className="text-sm text-muted-foreground">Due: {new Date(invoice.due_date).toLocaleDateString()}</p>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default Dashboard;
