import { useQuery } from '@tanstack/react-query';
import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { itemApi } from '@/lib/api';
import type { Item } from '@/types';

const Items = () => {
  const { data: items, isLoading } = useQuery({
    queryKey: ['items'],
    queryFn: itemApi.list,
  });

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Items</h1>
          <p className="mt-2 text-muted-foreground">Browse available items and products</p>
        </div>

        <Card className="shadow-soft">
          <CardHeader>
            <CardTitle>Available Items</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex justify-center py-12">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
              </div>
            ) : items?.length === 0 ? (
              <div className="py-12 text-center">
                <p className="text-muted-foreground">No items available</p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead className="text-right">Unit Price (Cash)</TableHead>
                    <TableHead className="text-right">Available Quantity</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {items?.map((item: Item) => (
                    <TableRow key={item.id}>
                      <TableCell className="font-medium">{item.name}</TableCell>
                      <TableCell className="text-muted-foreground">{item.description}</TableCell>
                      <TableCell className="text-right font-semibold">
                        {formatCurrency(item.unit_price_cash)}
                      </TableCell>
                      <TableCell className="text-right">{item.quantity_available}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default Items;
