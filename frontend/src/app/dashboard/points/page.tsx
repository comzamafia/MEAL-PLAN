"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { api, LoyaltyTransaction, ReferralInfo } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Star, Gift, Copy, Check } from "lucide-react";

export default function PointsPage() {
  const [balance, setBalance] = useState(0);
  const [dollarValue, setDollarValue] = useState("0.00");
  const [transactions, setTransactions] = useState<LoyaltyTransaction[]>([]);
  const [referral, setReferral] = useState<ReferralInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const didLoad = useRef(false);

  const loadData = useCallback(async () => {
    const [loyaltyRes, referralRes] = await Promise.all([
      api.getLoyaltyBalance(),
      api.getReferralLink(),
    ]);
    if (loyaltyRes.data) {
      setBalance(loyaltyRes.data.balance);
      setDollarValue(loyaltyRes.data.dollar_value);
      setTransactions(loyaltyRes.data.recent_transactions);
    }
    if (referralRes.data) {
      setReferral(referralRes.data);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    if (didLoad.current) return;
    didLoad.current = true;
    // eslint-disable-next-line react-hooks/set-state-in-effect -- Initial data fetch from API
    loadData();
  }, [loadData]);

  const copyReferralLink = async () => {
    if (!referral) return;
    await navigator.clipboard.writeText(referral.referral_url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const reasonLabels: Record<string, string> = {
    order_earned: "Order Reward",
    order_redeemed: "Points Redeemed",
    referral_bonus: "Referral Bonus",
    signup_bonus: "Welcome Bonus",
    admin_adjustment: "Adjustment",
    refund_deduction: "Refund",
    expiry: "Expired",
    promotional: "Promotion",
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 bg-gray-200 rounded animate-pulse" />
        <div className="h-40 bg-gray-200 rounded-lg animate-pulse" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Points & Referrals</h1>

      {/* Points Balance */}
      <Card className="bg-gradient-to-r from-yellow-50 to-orange-50 border-yellow-200">
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <div className="h-14 w-14 bg-yellow-100 rounded-full flex items-center justify-center">
              <Star className="h-7 w-7 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-yellow-700">Wela Points Balance</p>
              <p className="text-3xl font-bold text-yellow-900">
                {balance.toLocaleString()}
              </p>
              <p className="text-sm text-yellow-600">${dollarValue} value</p>
            </div>
          </div>
          <div className="mt-4 text-xs text-yellow-700 space-y-1">
            <p>Earn 10 points for every $1 spent</p>
            <p>100 points = $1 discount</p>
          </div>
        </CardContent>
      </Card>

      {/* Referral Section */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Gift className="h-5 w-5 text-green-600" />
            <CardTitle className="text-base">Refer a Friend</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-gray-600">
            Share your referral link and earn 500 points when your friend places their first order.
            They get 15% off!
          </p>

          {referral && (
            <>
              <div className="flex gap-2">
                <Input
                  readOnly
                  value={referral.referral_url}
                  className="text-sm"
                />
                <Button variant="outline" onClick={copyReferralLink} className="shrink-0">
                  {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                </Button>
              </div>

              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-xl font-bold">{referral.total_referrals}</p>
                  <p className="text-xs text-gray-500">Referrals</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-xl font-bold">{referral.pending_rewards}</p>
                  <p className="text-xs text-gray-500">Pending</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-xl font-bold">{referral.earned_points}</p>
                  <p className="text-xs text-gray-500">Points Earned</p>
                </div>
              </div>

              <p className="text-xs text-gray-400">
                Your referral code: <span className="font-mono font-medium">{referral.referral_code}</span>
              </p>
            </>
          )}
        </CardContent>
      </Card>

      {/* Transaction History */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Points History</CardTitle>
        </CardHeader>
        <CardContent>
          {transactions.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-6">
              No transactions yet. Start earning points by placing an order!
            </p>
          ) : (
            <div className="space-y-3">
              {transactions.map((tx) => (
                <div
                  key={tx.id}
                  className="flex items-center justify-between py-2 border-b last:border-0"
                >
                  <div>
                    <p className="text-sm font-medium">{tx.description}</p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <Badge variant="secondary" className="text-xs">
                        {reasonLabels[tx.reason] ?? tx.reason_display}
                      </Badge>
                      <span className="text-xs text-gray-400">
                        {new Date(tx.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <span
                    className={`text-sm font-semibold ${
                      tx.points_delta > 0 ? "text-green-600" : "text-red-600"
                    }`}
                  >
                    {tx.points_delta > 0 ? "+" : ""}
                    {tx.points_delta}
                  </span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
