export interface User {
  id: number;
  username: string;
  email: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterCredentials extends LoginCredentials {
  email: string;
  password2: string;
}

export interface Item {
  id: number;
  name: string;
  description: string;
  unit_price_cents: number;
  unit_price_cash: number;
}

export interface InvoiceLineItem {
  id?: number;
  item: number;
  item_name: string;
  quantity: number;
  unit_price_cents: number;
  unit_price_cash: number;
  total_price_cents: number;
  total_price_cash: number;
}

export interface Transaction {
  id: number;
  transaction_type: 'sale' | 'payment';
  amount_cents: number;
  amount_cash: number;
  notes: string;
  timestamp: string;
}

export interface Invoice {
  id: number;
  reference_number: string;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  customer_address: string;
  invoice_date: string;
  due_date: string;
  status: 'pending' | 'paid' | 'cancelled';
  total_amount: number;
  total_amount_cents: number;
  is_overdue: boolean;
  items_count?: number;
  items?: InvoiceLineItem[];
  transactions?: Transaction[];
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface CreateInvoiceRequest {
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  customer_address: string;
  due_date: string;
  items: Array<{
    item: number;
    quantity: number;
  }>;
}

export interface DashboardStats {
  total_invoices: number;
  pending_invoices: number;
  overdue_invoices: number;
  total_revenue: number;
}
