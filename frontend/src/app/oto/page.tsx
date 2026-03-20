"use client";

import { useState, useMemo, Suspense } from "react";
import { api } from "@/lib/api";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useSearchParams } from "next/navigation";
import {
  Clock,
  Zap,
  Star,
  ArrowRight,
  Gift,
  Truck,
} from "lucide-react";

const PLANS = [
  {
    id: "starter",
    name: "Starter Plan",
    meals: 5,
    priceWeekly: 49.99,
    pricePer: 10.0,
    savings: "0",
    features: ["5 meals per week", "Free delivery on orders $75+", "Earn 500 Wela Points/week"],
  },
  {
    id: "standard",
    name: "Standard Plan",
    meals: 10,
    priceWeekly: 89.99,
    pricePer: 9.0,
    savings: "10%",
    popular: true,
    features: ["10 meals per week", "FREE delivery every week", "Earn 900 Wela Points/week", "Priority ordering"],
  },
  {
    id: "premium",
    name: "Premium Plan",
    meals: 15,
    priceWeekly: 119.99,
    pricePer: 8.0,
    savings: "20%",
    features: ["15 meals per week", "FREE delivery every week", "Earn 1,200 Wela Points/week", "Priority ordering", "Exclusive dishes access"],
  },
];

function OTOContent() {
  const searchParams = useSearchParams();
  const orderNumber = searchParams.get("order") ?? "";
  const [selectedPlan, setSelectedPlan] = useState("standard");
  const [processing, setProcessing] = useState(false);
  const [declined, setDeclined] = useState(false);

  const plan = useMemo(() => PLANS.find((p) => p.id === selectedPlan)!, [selectedPlan]);

  const handleAccept = async () => {
    setProcessing(true);
    // In production: call api to add subscription via Stripe
    await api.confirmOrder(orderNumber);
    window.location.href = `/thank-you?order=${orderNumber}&subscription=${selectedPlan}`;
  };

  const handleDecline = () => {
    setDeclined(true);
    window.location.href = `/thank-you?order=${orderNumber}`;
  };

  return (
    <>
      <Header />
      <main className="min-h-screen bg-gradient-to-b from-green-50 to-white py-12">
        <div className="container mx-auto px-4 max-w-4xl">
          {/* Urgency bar */}
          <div className="bg-green-700 text-white px-4 py-3 rounded-lg mb-8 text-center flex items-center justify-center gap-2">
            <Clock className="h-5 w-5" />
            <span className="font-semibold">One-Time Offer — This will not be shown again!</span>
          </div>

          <div className="text-center mb-10">
            <Badge className="bg-green-100 text-green-700 mb-4">
              <Gift className="h-3 w-3 mr-1" />
              Exclusive Offer
            </Badge>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-3">
              Save Up To 20% with a Weekly Subscription
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              You just ordered some amazing Thai food! Lock in savings and never worry about meal prep again.
            </p>
          </div>

          {/* Plans */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
            {PLANS.map((p) => (
              <Card
                key={p.id}
                className={`cursor-pointer transition-all ${
                  selectedPlan === p.id
                    ? "ring-2 ring-green-600 shadow-lg"
                    : "hover:shadow-md"
                } ${p.popular ? "relative" : ""}`}
                onClick={() => setSelectedPlan(p.id)}
              >
                {p.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <Badge className="bg-green-600 text-white">Most Popular</Badge>
                  </div>
                )}
                <CardContent className="p-6 text-center space-y-4">
                  <h3 className="text-lg font-bold text-gray-900">{p.name}</h3>
                  <div>
                    <span className="text-3xl font-bold text-green-700">${p.priceWeekly}</span>
                    <span className="text-gray-500">/week</span>
                  </div>
                  <p className="text-sm text-gray-500">${p.pricePer.toFixed(2)} per meal</p>
                  {p.savings !== "0" && (
                    <Badge className="bg-orange-100 text-orange-700">Save {p.savings}</Badge>
                  )}
                  <Separator />
                  <ul className="text-sm text-gray-600 space-y-2 text-left">
                    {p.features.map((f) => (
                      <li key={f} className="flex items-start gap-2">
                        <Star className="h-4 w-4 text-green-600 shrink-0 mt-0.5" />
                        {f}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Benefits */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
            <div className="flex items-start gap-3 bg-white p-4 rounded-lg shadow-sm">
              <Zap className="h-6 w-6 text-green-600 shrink-0" />
              <div>
                <h4 className="font-semibold text-gray-900">Skip Anytime</h4>
                <p className="text-sm text-gray-500">Pause or skip weeks from your dashboard. No commitments.</p>
              </div>
            </div>
            <div className="flex items-start gap-3 bg-white p-4 rounded-lg shadow-sm">
              <Truck className="h-6 w-6 text-green-600 shrink-0" />
              <div>
                <h4 className="font-semibold text-gray-900">Free Delivery</h4>
                <p className="text-sm text-gray-500">Standard & Premium plans include free delivery every week.</p>
              </div>
            </div>
            <div className="flex items-start gap-3 bg-white p-4 rounded-lg shadow-sm">
              <Star className="h-6 w-6 text-green-600 shrink-0" />
              <div>
                <h4 className="font-semibold text-gray-900">Earn More Points</h4>
                <p className="text-sm text-gray-500">Subscribers earn 10 Wela Points per $1 on every delivery.</p>
              </div>
            </div>
          </div>

          {/* CTAs */}
          <div className="text-center space-y-4">
            <Button
              onClick={handleAccept}
              disabled={processing}
              className="bg-green-600 hover:bg-green-700 h-14 px-10 text-lg"
            >
              {processing ? "Setting up..." : `Subscribe to ${plan.name} — $${plan.priceWeekly}/week`}
              <ArrowRight className="h-5 w-5 ml-2" />
            </Button>
            <div>
              <button
                onClick={handleDecline}
                className="text-sm text-gray-400 hover:text-gray-600 underline"
                disabled={declined}
              >
                No thanks, I&apos;ll pay full price next time
              </button>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}

export default function OTOPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600" /></div>}>
      <OTOContent />
    </Suspense>
  );
}
