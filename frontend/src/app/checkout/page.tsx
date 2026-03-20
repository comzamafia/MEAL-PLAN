"use client";

import { useState } from "react";
import { useCartStore } from "@/lib/store";
import { api } from "@/lib/api";
import { useAuthStore } from "@/lib/auth-store";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
  Trash2,
  Minus,
  Plus,
  Lock,
  ShoppingBag,
  ArrowRight,
} from "lucide-react";
import Link from "next/link";
import Image from "next/image";

export default function CheckoutPage() {
  const {
    items,
    removeItem,
    updateQuantity,
    clearCart,
    setDeliveryAddress,
    couponCode,
    couponDiscount,
    setCoupon,
    getSubtotal,
    getDeliveryFee,
    getTaxAmount,
    getTotal,
    getTotalItems,
  } = useCartStore();

  const { user } = useAuthStore();
  const [step, setStep] = useState(1);
  const [couponInput, setCouponInput] = useState("");
  const [couponError, setCouponError] = useState("");
  const [couponLoading, setCouponLoading] = useState(false);
  const [processing, setProcessing] = useState(false);

  // Address form state
  const [address, setAddress] = useState({
    label: "Home",
    recipientName: user ? `${user.user.first_name} ${user.user.last_name}` : "",
    phone: user?.user.phone ?? "",
    streetAddress: "",
    unit: "",
    city: "Oakville",
    province: "ON",
    postalCode: "",
    deliveryInstructions: "",
  });

  const subtotal = getSubtotal();
  const deliveryFee = getDeliveryFee();
  const tax = getTaxAmount();
  const total = getTotal();
  const totalItems = getTotalItems();

  const handleApplyCoupon = async () => {
    if (!couponInput.trim()) return;
    setCouponLoading(true);
    setCouponError("");
    const res = await api.validateCoupon(couponInput.trim(), subtotal);
    if (res.data?.valid) {
      setCoupon(couponInput.trim(), parseFloat(res.data.discount_amount));
    } else {
      setCouponError("Invalid coupon code");
    }
    setCouponLoading(false);
  };

  const handlePlaceOrder = async () => {
    setProcessing(true);
    // Save delivery address to store
    setDeliveryAddress(address);

    const res = await api.createPaymentIntent({
      items: items.map((i) => ({
        menu_item_id: i.menuItem.id,
        quantity: i.quantity,
        modifiers: i.modifiers.map((m) => m.id),
      })),
      delivery_address: {
        name: address.recipientName,
        street_address: address.streetAddress,
        city: address.city,
        province: address.province,
        postal_code: address.postalCode,
        phone: address.phone,
        delivery_instructions: address.deliveryInstructions,
      },
      delivery_window_id: "",
      coupon_code: couponCode ?? undefined,
    });

    if (res.data?.client_secret) {
      // In production: use Stripe Elements to confirm payment
      // For now, simulate confirmation
      const confirmRes = await api.confirmOrder(res.data.client_secret);
      if (confirmRes.data?.order_number) {
        clearCart();
        window.location.href = `/thank-you?order=${confirmRes.data.order_number}`;
        return;
      }
    }

    // Fallback: simulate success for demo
    clearCart();
    window.location.href = "/thank-you?order=WMP-DEMO-0001";
  };

  if (totalItems === 0) {
    return (
      <>
        <Header />
        <main className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center space-y-4">
            <ShoppingBag className="h-16 w-16 text-gray-300 mx-auto" />
            <h2 className="text-2xl font-bold text-gray-900">Your cart is empty</h2>
            <p className="text-gray-500">Browse our menu and add some delicious Thai meals!</p>
            <Link href="/menu">
              <Button className="bg-green-600 hover:bg-green-700">
                Browse Menu
              </Button>
            </Link>
          </div>
        </main>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Header />
      <main className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4 max-w-5xl">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Checkout</h1>

          {/* Steps indicator */}
          <div className="flex items-center gap-4 mb-8">
            <div className={`flex items-center gap-2 ${step >= 1 ? "text-green-700" : "text-gray-400"}`}>
              <span className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${step >= 1 ? "bg-green-600 text-white" : "bg-gray-200"}`}>
                1
              </span>
              <span className="font-medium">Review Cart</span>
            </div>
            <div className="flex-1 h-px bg-gray-300" />
            <div className={`flex items-center gap-2 ${step >= 2 ? "text-green-700" : "text-gray-400"}`}>
              <span className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${step >= 2 ? "bg-green-600 text-white" : "bg-gray-200"}`}>
                2
              </span>
              <span className="font-medium">Delivery & Payment</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left column */}
            <div className="lg:col-span-2 space-y-6">
              {step === 1 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Your Cart ({totalItems} items)</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {items.map((item) => (
                      <div key={item.menuItem.id} className="flex items-center gap-4 py-3 border-b last:border-0">
                        <div className="w-16 h-16 bg-green-100 rounded-lg flex items-center justify-center shrink-0">
                          {item.menuItem.image_url ? (
                            <Image src={item.menuItem.image_url} alt={item.menuItem.name_en} width={64} height={64} className="w-full h-full object-cover rounded-lg" unoptimized />
                          ) : (
                            <span className="text-2xl">🍲</span>
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium text-gray-900 truncate">{item.menuItem.name_en}</h4>
                          <p className="text-sm text-gray-500">{item.menuItem.calories} cal | {item.menuItem.protein_g}g protein</p>
                          {item.modifiers.length > 0 && (
                            <p className="text-xs text-gray-400">
                              {item.modifiers.map((m) => m.name_en).join(", ")}
                            </p>
                          )}
                        </div>
                        <div className="flex items-center gap-2">
                          <Button size="icon-xs" variant="outline" onClick={() => updateQuantity(item.menuItem.id, item.quantity - 1)}>
                            <Minus className="h-3 w-3" />
                          </Button>
                          <span className="w-8 text-center font-medium text-sm">{item.quantity}</span>
                          <Button size="icon-xs" variant="outline" onClick={() => updateQuantity(item.menuItem.id, item.quantity + 1)}>
                            <Plus className="h-3 w-3" />
                          </Button>
                        </div>
                        <span className="font-semibold text-gray-900 w-16 text-right">
                          ${(item.menuItem.base_price * item.quantity).toFixed(2)}
                        </span>
                        <Button size="icon-xs" variant="ghost" onClick={() => removeItem(item.menuItem.id)}>
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    ))}

                    {/* Coupon */}
                    <div className="pt-4">
                      {couponCode ? (
                        <div className="flex items-center justify-between bg-green-50 p-3 rounded-lg">
                          <div>
                            <Badge className="bg-green-100 text-green-700">{couponCode}</Badge>
                            <span className="text-sm text-green-700 ml-2">-${couponDiscount.toFixed(2)}</span>
                          </div>
                          <Button size="xs" variant="ghost" onClick={() => setCoupon(null, 0)}>Remove</Button>
                        </div>
                      ) : (
                        <div className="flex gap-2">
                          <Input
                            placeholder="Coupon code"
                            value={couponInput}
                            onChange={(e) => setCouponInput(e.target.value.toUpperCase())}
                            className="flex-1"
                          />
                          <Button variant="outline" onClick={handleApplyCoupon} disabled={couponLoading}>
                            {couponLoading ? "..." : "Apply"}
                          </Button>
                        </div>
                      )}
                      {couponError && <p className="text-sm text-red-600 mt-1">{couponError}</p>}
                    </div>

                    <Button onClick={() => setStep(2)} className="w-full bg-green-600 hover:bg-green-700">
                      Continue to Delivery
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Button>
                  </CardContent>
                </Card>
              )}

              {step === 2 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Delivery Address</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="recipientName">Full Name</Label>
                        <Input
                          id="recipientName"
                          value={address.recipientName}
                          onChange={(e) => setAddress({ ...address, recipientName: e.target.value })}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="phone">Phone</Label>
                        <Input
                          id="phone"
                          type="tel"
                          value={address.phone}
                          onChange={(e) => setAddress({ ...address, phone: e.target.value })}
                          required
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                      <div className="col-span-2">
                        <Label htmlFor="street">Street Address</Label>
                        <Input
                          id="street"
                          value={address.streetAddress}
                          onChange={(e) => setAddress({ ...address, streetAddress: e.target.value })}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="unit">Unit/Apt</Label>
                        <Input
                          id="unit"
                          value={address.unit}
                          onChange={(e) => setAddress({ ...address, unit: e.target.value })}
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <Label htmlFor="city">City</Label>
                        <Input
                          id="city"
                          value={address.city}
                          onChange={(e) => setAddress({ ...address, city: e.target.value })}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="province">Province</Label>
                        <Input id="province" value={address.province} disabled />
                      </div>
                      <div>
                        <Label htmlFor="postal">Postal Code</Label>
                        <Input
                          id="postal"
                          value={address.postalCode}
                          onChange={(e) => setAddress({ ...address, postalCode: e.target.value.toUpperCase() })}
                          placeholder="L6H 1A1"
                          required
                        />
                      </div>
                    </div>

                    <div>
                      <Label htmlFor="instructions">Delivery Instructions (optional)</Label>
                      <Input
                        id="instructions"
                        value={address.deliveryInstructions}
                        onChange={(e) => setAddress({ ...address, deliveryInstructions: e.target.value })}
                        placeholder="e.g., Leave at side door, buzz #204..."
                      />
                    </div>

                    <Separator />

                    {/* Payment placeholder */}
                    <div className="bg-gray-50 rounded-lg p-6 text-center">
                      <Lock className="h-6 w-6 text-gray-400 mx-auto mb-2" />
                      <p className="text-sm text-gray-500 mb-1">Secure Payment via Stripe</p>
                      <p className="text-xs text-gray-400">Card details will appear here when Stripe is connected</p>
                    </div>

                    <div className="flex gap-3">
                      <Button variant="outline" onClick={() => setStep(1)} className="flex-1">
                        Back to Cart
                      </Button>
                      <Button
                        onClick={handlePlaceOrder}
                        disabled={processing || !address.recipientName || !address.streetAddress || !address.postalCode}
                        className="flex-1 bg-green-600 hover:bg-green-700"
                      >
                        {processing ? "Processing..." : `Place Order - $${total.toFixed(2)}`}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Right column - Order Summary */}
            <div>
              <Card className="sticky top-4">
                <CardHeader>
                  <CardTitle className="text-base">Order Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {items.map((item) => (
                    <div key={item.menuItem.id} className="flex justify-between text-sm">
                      <span className="text-gray-600">
                        {item.menuItem.name_en} x{item.quantity}
                      </span>
                      <span className="font-medium">
                        ${(item.menuItem.base_price * item.quantity).toFixed(2)}
                      </span>
                    </div>
                  ))}

                  <Separator />

                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Subtotal</span>
                    <span>${subtotal.toFixed(2)}</span>
                  </div>
                  {couponDiscount > 0 && (
                    <div className="flex justify-between text-sm text-green-600">
                      <span>Coupon ({couponCode})</span>
                      <span>-${couponDiscount.toFixed(2)}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Delivery</span>
                    <span>{deliveryFee === 0 ? "FREE" : `$${deliveryFee.toFixed(2)}`}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">HST (13%)</span>
                    <span>${tax.toFixed(2)}</span>
                  </div>

                  <Separator />

                  <div className="flex justify-between font-bold text-lg">
                    <span>Total</span>
                    <span className="text-green-700">${total.toFixed(2)}</span>
                  </div>

                  <p className="text-xs text-gray-400 text-center pt-2">
                    Earn {Math.floor(subtotal * 10)} Wela Points with this order
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
