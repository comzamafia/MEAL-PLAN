"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { useCartStore } from "@/lib/store";

export function CheckoutSection() {
  const [step, setStep] = useState<1 | 2>(1);
  const [postalCode, setPostalCode] = useState("");
  const [postalValid, setPostalValid] = useState<boolean | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [couponCode, setCouponCode] = useState("");

  const {
    items,
    getSubtotal,
    getDeliveryFee,
    getTaxAmount,
    getTotal,
    getTotalItems,
    updateQuantity,
    deliveryZone,
    setDeliveryZone,
  } = useCartStore();

  const handlePostalValidation = async () => {
    if (postalCode.length < 3) return;

    setIsValidating(true);
    // Simulate API call - in production, this would call the backend
    setTimeout(() => {
      const validPrefixes = ["L6H", "L6J", "L6K", "L6L", "L6M", "L7L", "L7M", "L7N", "L7P", "L7R", "L7S", "L7T", "L9T"];
      const prefix = postalCode.toUpperCase().substring(0, 3);
      const isValid = validPrefixes.includes(prefix);

      setPostalValid(isValid);
      if (isValid) {
        setDeliveryZone({
          id: "1",
          postal_code_prefix: prefix,
          label: "Oakville / Burlington",
          delivery_fee: 5.99,
          free_delivery_threshold: 75,
        });
      }
      setIsValidating(false);
    }, 500);
  };

  return (
    <section id="checkout" className="py-16 md:py-24 bg-white">
      <div className="container px-4 md:px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
            Complete Your Order
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Order by Friday 5 PM for Sunday delivery.
          </p>
        </div>

        <div className="grid gap-8 lg:grid-cols-3">
          {/* Checkout Form */}
          <div className="lg:col-span-2 space-y-6">
            {/* Step Indicator */}
            <div className="flex items-center gap-4 mb-8">
              <div
                className={`flex h-10 w-10 items-center justify-center rounded-full ${
                  step >= 1
                    ? "bg-green-600 text-white"
                    : "bg-gray-200 text-gray-600"
                }`}
              >
                1
              </div>
              <div className="flex-1 h-1 bg-gray-200">
                <div
                  className={`h-full transition-all ${
                    step >= 2 ? "bg-green-600 w-full" : "w-0"
                  }`}
                />
              </div>
              <div
                className={`flex h-10 w-10 items-center justify-center rounded-full ${
                  step >= 2
                    ? "bg-green-600 text-white"
                    : "bg-gray-200 text-gray-600"
                }`}
              >
                2
              </div>
            </div>

            {/* Step 1: Delivery Information */}
            {step === 1 && (
              <Card>
                <CardHeader>
                  <CardTitle>Step 1: Delivery Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Postal Code Validation */}
                  <div className="space-y-2">
                    <Label htmlFor="postal">
                      Postal Code <span className="text-red-500">*</span>
                    </Label>
                    <div className="flex gap-2">
                      <Input
                        id="postal"
                        placeholder="L6H 1A1"
                        value={postalCode}
                        onChange={(e) => {
                          setPostalCode(e.target.value.toUpperCase());
                          setPostalValid(null);
                        }}
                        className="max-w-[200px]"
                      />
                      <Button
                        variant="outline"
                        onClick={handlePostalValidation}
                        disabled={isValidating || postalCode.length < 3}
                      >
                        {isValidating ? "Checking..." : "Check Delivery"}
                      </Button>
                    </div>
                    {postalValid === true && (
                      <p className="text-sm text-green-600 flex items-center gap-1">
                        <svg
                          className="h-4 w-4"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                        Great! We deliver to your area. Delivery fee: $
                        {deliveryZone?.delivery_fee.toFixed(2)}
                        {getSubtotal() >= (deliveryZone?.free_delivery_threshold || 75) && (
                          <span className="font-medium"> (FREE - order over ${deliveryZone?.free_delivery_threshold}!)</span>
                        )}
                      </p>
                    )}
                    {postalValid === false && (
                      <p className="text-sm text-red-600">
                        Sorry, we don&apos;t deliver to this area yet. We currently
                        serve Oakville, Burlington, and Milton.
                      </p>
                    )}
                  </div>

                  {postalValid && (
                    <>
                      <Separator />

                      <div className="grid gap-4 md:grid-cols-2">
                        <div className="space-y-2">
                          <Label htmlFor="name">Full Name</Label>
                          <Input id="name" placeholder="John Doe" />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="phone">Phone Number</Label>
                          <Input id="phone" placeholder="(416) 555-1234" />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="address">Street Address</Label>
                        <Input id="address" placeholder="123 Main Street" />
                      </div>

                      <div className="grid gap-4 md:grid-cols-3">
                        <div className="space-y-2">
                          <Label htmlFor="unit">Unit/Apt (Optional)</Label>
                          <Input id="unit" placeholder="Apt 4B" />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="city">City</Label>
                          <Input id="city" defaultValue="Oakville" />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="province">Province</Label>
                          <Input id="province" defaultValue="Ontario" disabled />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="instructions">
                          Delivery Instructions (Optional)
                        </Label>
                        <Input
                          id="instructions"
                          placeholder="Leave at front door, ring bell, etc."
                        />
                      </div>

                      <Button
                        className="w-full bg-green-600 hover:bg-green-700"
                        size="lg"
                        onClick={() => setStep(2)}
                        disabled={items.length === 0}
                      >
                        Continue to Payment
                        <svg
                          className="ml-2 h-5 w-5"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M13 7l5 5m0 0l-5 5m5-5H6"
                          />
                        </svg>
                      </Button>
                    </>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Step 2: Payment */}
            {step === 2 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>Step 2: Payment</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setStep(1)}
                    >
                      ← Back
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Coupon Code */}
                  <div className="space-y-2">
                    <Label htmlFor="coupon">Coupon Code (Optional)</Label>
                    <div className="flex gap-2">
                      <Input
                        id="coupon"
                        placeholder="Enter code"
                        value={couponCode}
                        onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
                      />
                      <Button variant="outline">Apply</Button>
                    </div>
                  </div>

                  <Separator />

                  {/* Stripe Elements Placeholder */}
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label>Card Information</Label>
                      <div className="border rounded-lg p-4 bg-gray-50">
                        <p className="text-sm text-gray-500 text-center">
                          Stripe Payment Form will be integrated here
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <svg
                        className="h-5 w-5 text-green-600"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                        />
                      </svg>
                      Your payment is secured by Stripe
                    </div>
                  </div>

                  {/* Order Bump */}
                  <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <input
                        type="checkbox"
                        id="order-bump"
                        className="mt-1 h-5 w-5 rounded border-gray-300"
                      />
                      <div className="flex-1">
                        <label
                          htmlFor="order-bump"
                          className="font-semibold text-yellow-800 cursor-pointer"
                        >
                          ADD: Bulk Basil Chicken Breast (300g) - Only $8.99!
                        </label>
                        <p className="text-sm text-yellow-700 mt-1">
                          Perfect for adding extra protein to your meals. 180 cal, 38g protein.
                          <span className="font-medium"> Save $3 vs. regular price!</span>
                        </p>
                      </div>
                    </div>
                  </div>

                  <Button
                    className="w-full bg-green-600 hover:bg-green-700"
                    size="lg"
                  >
                    Pay ${getTotal().toFixed(2)}
                    <svg
                      className="ml-2 h-5 w-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                      />
                    </svg>
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <Card className="sticky top-24">
              <CardHeader>
                <CardTitle>Order Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {items.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">
                    Your cart is empty. Add some meals above!
                  </p>
                ) : (
                  <>
                    {/* Cart Items */}
                    <div className="space-y-3 max-h-[300px] overflow-y-auto">
                      {items.map((item) => (
                        <div
                          key={item.menuItem.id}
                          className="flex items-center gap-3"
                        >
                          <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center text-xl">
                            🍱
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-sm truncate">
                              {item.menuItem.name_en}
                            </p>
                            <p className="text-xs text-gray-500">
                              ${item.menuItem.base_price.toFixed(2)} each
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() =>
                                updateQuantity(item.menuItem.id, item.quantity - 1)
                              }
                              className="h-6 w-6 rounded border text-sm hover:bg-gray-100"
                            >
                              -
                            </button>
                            <span className="text-sm w-6 text-center">
                              {item.quantity}
                            </span>
                            <button
                              onClick={() =>
                                updateQuantity(item.menuItem.id, item.quantity + 1)
                              }
                              className="h-6 w-6 rounded border text-sm hover:bg-gray-100"
                            >
                              +
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>

                    <Separator />

                    {/* Totals */}
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Subtotal</span>
                        <span>${getSubtotal().toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Delivery</span>
                        <span>
                          {getDeliveryFee() === 0 ? (
                            <span className="text-green-600">FREE</span>
                          ) : (
                            `$${getDeliveryFee().toFixed(2)}`
                          )}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">HST (13%)</span>
                        <span>${getTaxAmount().toFixed(2)}</span>
                      </div>
                    </div>

                    <Separator />

                    <div className="flex justify-between font-semibold text-lg">
                      <span>Total</span>
                      <span className="text-green-600">
                        ${getTotal().toFixed(2)}
                      </span>
                    </div>

                    {/* Nutrition Summary */}
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-xs text-gray-500 mb-2">
                        Weekly Nutrition Summary
                      </p>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <span className="text-gray-600">Meals:</span>{" "}
                          <span className="font-medium">{getTotalItems()}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Calories:</span>{" "}
                          <span className="font-medium">
                            {items.reduce(
                              (sum, item) =>
                                sum + item.menuItem.calories * item.quantity,
                              0
                            )}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Protein:</span>{" "}
                          <span className="font-medium">
                            {items.reduce(
                              (sum, item) =>
                                sum + item.menuItem.protein_g * item.quantity,
                              0
                            )}
                            g
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Points Earned */}
                    <div className="flex items-center gap-2 text-sm text-green-600 bg-green-50 p-3 rounded-lg">
                      <svg
                        className="h-5 w-5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      Earn {Math.floor(getSubtotal() * 10)} Wela Points on this
                      order!
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
}
