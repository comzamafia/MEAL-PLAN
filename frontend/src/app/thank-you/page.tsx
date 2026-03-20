"use client";

import { useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { useAuthStore } from "@/lib/auth-store";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  CheckCircle,
  Gift,
  Copy,
  Check,
  Star,
  Share2,
} from "lucide-react";
import Link from "next/link";

function ThankYouContent() {
  const searchParams = useSearchParams();
  const orderNumber = searchParams.get("order") ?? "WMP-DEMO-0001";
  const subscriptionPlan = searchParams.get("subscription");
  const { user } = useAuthStore();
  const [copied, setCopied] = useState(false);

  const referralCode = user?.referral_code ?? "WELAXXXX";
  const referralUrl = `https://welamealprep.ca/?ref=${referralCode}`;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(referralUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-green-50 to-white py-12">
      <div className="container mx-auto px-4 max-w-2xl">
        {/* Success header */}
        <div className="text-center mb-10">
          <CheckCircle className="h-16 w-16 text-green-600 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Order Confirmed!</h1>
          <p className="text-lg text-gray-600">
            Thank you for your order. Your Thai meals are being prepared with love.
          </p>
        </div>

        {/* Order details */}
        <Card className="mb-6">
          <CardContent className="p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Order Number</p>
                <p className="text-lg font-bold text-gray-900">{orderNumber}</p>
              </div>
              <Badge className="bg-green-100 text-green-700">Confirmed</Badge>
            </div>

            {subscriptionPlan && (
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <Star className="h-4 w-4 text-green-600" />
                  <span className="font-semibold text-green-800">
                    Subscription Active: {subscriptionPlan.charAt(0).toUpperCase() + subscriptionPlan.slice(1)} Plan
                  </span>
                </div>
                <p className="text-sm text-green-700">
                  Manage your subscription anytime from your{" "}
                  <Link href="/dashboard/subscription" className="underline font-medium">
                    dashboard
                  </Link>
                  .
                </p>
              </div>
            )}

            <div className="grid grid-cols-3 gap-4 text-center text-sm">
              <div className="bg-gray-50 p-3 rounded-lg">
                <p className="text-gray-500">Status</p>
                <p className="font-semibold">Being Prepared</p>
              </div>
              <div className="bg-gray-50 p-3 rounded-lg">
                <p className="text-gray-500">Delivery</p>
                <p className="font-semibold">This Sunday</p>
              </div>
              <div className="bg-gray-50 p-3 rounded-lg">
                <p className="text-gray-500">Points Earned</p>
                <p className="font-semibold text-green-600">+150</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Referral section */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <Gift className="h-5 w-5 text-green-600" />
              <h2 className="text-lg font-bold">Share & Earn 500 Points</h2>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Give your friends 15% off their first order. You&apos;ll earn 500 Wela Points (worth $5.00) for every friend who orders!
            </p>

            <div className="flex gap-2 mb-4">
              <Input
                value={referralUrl}
                readOnly
                className="flex-1 text-sm bg-gray-50"
              />
              <Button variant="outline" onClick={handleCopy}>
                {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              </Button>
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                className="flex-1"
                onClick={() => {
                  window.open(
                    `https://wa.me/?text=${encodeURIComponent(`Get 15% off your first Wela Meal Prep order! ${referralUrl}`)}`,
                    "_blank"
                  );
                }}
              >
                <Share2 className="h-4 w-4 mr-1" />
                WhatsApp
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="flex-1"
                onClick={() => {
                  window.open(
                    `mailto:?subject=${encodeURIComponent("Try Wela Meal Prep!")}&body=${encodeURIComponent(`Get 15% off your first order of authentic Thai meal prep: ${referralUrl}`)}`,
                    "_blank"
                  );
                }}
              >
                Email a Friend
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* What happens next */}
        <Card className="mb-8">
          <CardContent className="p-6">
            <h2 className="font-bold text-gray-900 mb-4">What Happens Next?</h2>
            <ol className="space-y-3">
              {[
                { step: "1", text: "You\u2019ll receive an email confirmation shortly" },
                { step: "2", text: "Our kitchen prepares your meals fresh Saturday & Sunday" },
                { step: "3", text: "Delivery arrives to your door on Sunday" },
                { step: "4", text: "Enjoy meals all week \u2014 just heat and eat!" },
              ].map((item) => (
                <li key={item.step} className="flex items-start gap-3">
                  <span className="w-6 h-6 bg-green-600 text-white text-xs font-bold rounded-full flex items-center justify-center shrink-0">
                    {item.step}
                  </span>
                  <span className="text-sm text-gray-700">{item.text}</span>
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3">
          <Link href="/dashboard" className="flex-1">
            <Button variant="outline" className="w-full">View Dashboard</Button>
          </Link>
          <Link href="/menu" className="flex-1">
            <Button className="w-full bg-green-600 hover:bg-green-700">Browse More Meals</Button>
          </Link>
        </div>
      </div>
    </main>
  );
}

export default function ThankYouPage() {
  return (
    <>
      <Header />
      <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600" /></div>}>
        <ThankYouContent />
      </Suspense>
      <Footer />
    </>
  );
}
