"use client";

import { useEffect, useState, useRef } from "react";
import { useAuthStore } from "@/lib/auth-store";
import { api, OrderData, SubscriptionData } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import {
  ShoppingBag,
  Star,
  RefreshCw,
  TrendingUp,
  ChevronRight,
} from "lucide-react";

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [orders, setOrders] = useState<OrderData[]>([]);
  const [subscription, setSubscription] = useState<SubscriptionData | null>(null);
  const [loading, setLoading] = useState(true);
  const didLoad = useRef(false);

  useEffect(() => {
    if (didLoad.current) return;
    didLoad.current = true;
    async function load() {
      const [ordersRes, subRes] = await Promise.all([
        api.getOrders(),
        api.getSubscription(),
      ]);
      if (ordersRes.data) setOrders(ordersRes.data);
      if (subRes.data) setSubscription(subRes.data);
      setLoading(false);
    }
    load();
  }, []);

  const recentOrders = orders.slice(0, 3);
  const totalSpent = orders.reduce((sum, o) => sum + parseFloat(o.total), 0);
  const totalPoints = user?.wela_points_balance ?? 0;

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 bg-gray-200 rounded animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 bg-gray-200 rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.user.first_name}!
        </h1>
        <p className="text-gray-500 mt-1">
          Here&apos;s what&apos;s happening with your meal prep.
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Orders</p>
                <p className="text-2xl font-bold">{orders.length}</p>
              </div>
              <div className="h-10 w-10 bg-blue-50 rounded-full flex items-center justify-center">
                <ShoppingBag className="h-5 w-5 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Wela Points</p>
                <p className="text-2xl font-bold">{totalPoints.toLocaleString()}</p>
                <p className="text-xs text-gray-400">${(totalPoints / 100).toFixed(2)} value</p>
              </div>
              <div className="h-10 w-10 bg-yellow-50 rounded-full flex items-center justify-center">
                <Star className="h-5 w-5 text-yellow-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Spent</p>
                <p className="text-2xl font-bold">${totalSpent.toFixed(2)}</p>
              </div>
              <div className="h-10 w-10 bg-green-50 rounded-full flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Subscription Status */}
      {subscription && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <CardTitle className="text-base">Active Subscription</CardTitle>
            <Link href="/dashboard/subscription">
              <Button variant="ghost" size="sm">
                Manage <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <div className="h-10 w-10 bg-green-50 rounded-full flex items-center justify-center">
                <RefreshCw className="h-5 w-5 text-green-600" />
              </div>
              <div className="flex-1">
                <p className="font-medium">{subscription.plan_type_display}</p>
                <p className="text-sm text-gray-500">
                  {subscription.billing_cycle} &middot; ${subscription.price_per_cycle}/cycle
                </p>
              </div>
              <Badge
                variant={subscription.status === "active" ? "default" : "secondary"}
                className={subscription.status === "active" ? "bg-green-100 text-green-700" : ""}
              >
                {subscription.status_display}
              </Badge>
            </div>
            {subscription.next_billing_date && (
              <p className="text-xs text-gray-400 mt-3">
                Next billing: {new Date(subscription.next_billing_date).toLocaleDateString()}
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {!subscription && (
        <Card>
          <CardContent className="pt-6 text-center">
            <RefreshCw className="h-8 w-8 text-gray-300 mx-auto mb-3" />
            <p className="font-medium text-gray-700">No Active Subscription</p>
            <p className="text-sm text-gray-500 mt-1">
              Subscribe to get weekly meal prep delivered to your door.
            </p>
            <Link href="/">
              <Button className="mt-4 bg-green-600 hover:bg-green-700" size="sm">
                Browse Menu
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {/* Recent Orders */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-3">
          <CardTitle className="text-base">Recent Orders</CardTitle>
          <Link href="/dashboard/orders">
            <Button variant="ghost" size="sm">
              View All <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </Link>
        </CardHeader>
        <CardContent>
          {recentOrders.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">No orders yet.</p>
          ) : (
            <div className="space-y-3">
              {recentOrders.map((order) => (
                <div
                  key={order.id}
                  className="flex items-center justify-between py-2 border-b last:border-0"
                >
                  <div>
                    <p className="text-sm font-medium">{order.order_number}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(order.created_at).toLocaleDateString()} &middot;{" "}
                      {order.items.length} item{order.items.length !== 1 ? "s" : ""}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">${order.total}</p>
                    <Badge variant="outline" className="text-xs capitalize">
                      {order.status_display}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
