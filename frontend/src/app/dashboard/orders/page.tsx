"use client";

import { useEffect, useState, useRef } from "react";
import { api, OrderData } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ShoppingBag } from "lucide-react";

const statusColors: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-700",
  confirmed: "bg-blue-100 text-blue-700",
  prep: "bg-purple-100 text-purple-700",
  ready: "bg-indigo-100 text-indigo-700",
  out_for_delivery: "bg-cyan-100 text-cyan-700",
  delivered: "bg-green-100 text-green-700",
  cancelled: "bg-red-100 text-red-700",
  refunded: "bg-gray-100 text-gray-700",
};

export default function OrdersPage() {
  const [orders, setOrders] = useState<OrderData[]>([]);
  const [loading, setLoading] = useState(true);
  const didLoad = useRef(false);

  useEffect(() => {
    if (didLoad.current) return;
    didLoad.current = true;
    async function load() {
      const res = await api.getOrders();
      if (res.data) setOrders(res.data);
      setLoading(false);
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-40 bg-gray-200 rounded animate-pulse" />
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 bg-gray-200 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Order History</h1>
        <p className="text-gray-500 mt-1">View all your past and current orders.</p>
      </div>

      {orders.length === 0 ? (
        <Card>
          <CardContent className="pt-6 text-center py-12">
            <ShoppingBag className="h-10 w-10 text-gray-300 mx-auto mb-3" />
            <p className="font-medium text-gray-700">No orders yet</p>
            <p className="text-sm text-gray-500 mt-1">
              Your order history will appear here after your first purchase.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => {
            return (
              <Card key={order.id}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">{order.order_number}</CardTitle>
                    <Badge className={statusColors[order.status] ?? "bg-gray-100 text-gray-700"}>
                      {order.status_display}
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-500">
                    {new Date(order.created_at).toLocaleDateString("en-CA", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    })}
                    {order.delivery_window_display && ` \u00B7 ${order.delivery_window_display}`}
                  </p>
                </CardHeader>
                <CardContent>
                  {/* Order items */}
                  <div className="space-y-2 mb-4">
                    {order.items.map((item) => (
                      <div key={item.id} className="flex justify-between text-sm">
                        <span>
                          {item.quantity}x {item.menu_item_name}
                        </span>
                        <span className="text-gray-600">${item.subtotal}</span>
                      </div>
                    ))}
                  </div>

                  {/* Order totals */}
                  <div className="border-t pt-3 space-y-1 text-sm">
                    <div className="flex justify-between text-gray-500">
                      <span>Subtotal</span>
                      <span>${order.subtotal}</span>
                    </div>
                    {parseFloat(order.discount_amount) > 0 && (
                      <div className="flex justify-between text-green-600">
                        <span>Discount</span>
                        <span>-${order.discount_amount}</span>
                      </div>
                    )}
                    <div className="flex justify-between text-gray-500">
                      <span>Delivery</span>
                      <span>${order.delivery_fee}</span>
                    </div>
                    <div className="flex justify-between text-gray-500">
                      <span>HST ({(parseFloat(order.tax_rate) * 100).toFixed(0)}%)</span>
                      <span>${order.tax_amount}</span>
                    </div>
                    <div className="flex justify-between font-semibold pt-1 border-t">
                      <span>Total</span>
                      <span>${order.total}</span>
                    </div>
                    {order.points_earned > 0 && (
                      <p className="text-xs text-yellow-600 mt-1">
                        +{order.points_earned} Wela Points earned
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
