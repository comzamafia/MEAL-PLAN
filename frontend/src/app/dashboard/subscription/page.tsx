"use client";

import { useEffect, useState, useCallback, useMemo, useRef } from "react";
import { api, SubscriptionData } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { RefreshCw, Pause, Play, X, SkipForward } from "lucide-react";
import Link from "next/link";

export default function SubscriptionPage() {
  const [sub, setSub] = useState<SubscriptionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const didLoad = useRef(false);

  // Precompute min dates to avoid Date.now() in render
  const minPauseDate = useMemo(() => {
    const d = new Date();
    d.setDate(d.getDate() + 7);
    return d.toISOString().split("T")[0];
  }, []);
  const minSkipDate = useMemo(() => {
    const d = new Date();
    d.setDate(d.getDate() + 3);
    return d.toISOString().split("T")[0];
  }, []);

  // Dialogs
  const [pauseOpen, setPauseOpen] = useState(false);
  const [cancelOpen, setCancelOpen] = useState(false);
  const [skipOpen, setSkipOpen] = useState(false);
  const [pauseDate, setPauseDate] = useState("");
  const [cancelReason, setCancelReason] = useState("");
  const [skipDate, setSkipDate] = useState("");

  const loadSubscription = useCallback(async () => {
    const res = await api.getSubscription();
    setSub(res.data ?? null);
    setLoading(false);
  }, []);

  useEffect(() => {
    if (didLoad.current) return;
    didLoad.current = true;
    // eslint-disable-next-line react-hooks/set-state-in-effect -- Initial data fetch from API
    loadSubscription();
  }, [loadSubscription]);

  const handlePause = async () => {
    if (!pauseDate) return;
    setActionLoading(true);
    await api.pauseSubscription(pauseDate);
    setPauseOpen(false);
    await loadSubscription();
    setActionLoading(false);
  };

  const handleResume = async () => {
    setActionLoading(true);
    await api.resumeSubscription();
    await loadSubscription();
    setActionLoading(false);
  };

  const handleCancel = async () => {
    setActionLoading(true);
    await api.cancelSubscription(cancelReason);
    setCancelOpen(false);
    await loadSubscription();
    setActionLoading(false);
  };

  const handleSkip = async () => {
    if (!skipDate) return;
    setActionLoading(true);
    await api.skipWeek(skipDate);
    setSkipOpen(false);
    await loadSubscription();
    setActionLoading(false);
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 bg-gray-200 rounded animate-pulse" />
        <div className="h-64 bg-gray-200 rounded-lg animate-pulse" />
      </div>
    );
  }

  if (!sub) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Subscription</h1>
        <Card>
          <CardContent className="pt-6 text-center py-12">
            <RefreshCw className="h-10 w-10 text-gray-300 mx-auto mb-3" />
            <p className="font-medium text-gray-700">No Active Subscription</p>
            <p className="text-sm text-gray-500 mt-1 max-w-sm mx-auto">
              Start a subscription to get fresh meal prep delivered weekly to your door.
            </p>
            <Link href="/">
              <Button className="mt-4 bg-green-600 hover:bg-green-700">
                Browse Menu
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  const isActive = sub.status === "active";
  const isPaused = sub.status === "paused";

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Subscription</h1>

      {/* Status Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Plan Details</CardTitle>
            <Badge
              className={
                isActive
                  ? "bg-green-100 text-green-700"
                  : isPaused
                    ? "bg-yellow-100 text-yellow-700"
                    : "bg-gray-100 text-gray-700"
              }
            >
              {sub.status_display}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">Plan</p>
              <p className="font-medium">{sub.plan_type_display}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Billing Cycle</p>
              <p className="font-medium capitalize">{sub.billing_cycle}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Price per Cycle</p>
              <p className="font-medium">${sub.price_per_cycle}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Next Billing</p>
              <p className="font-medium">
                {sub.next_billing_date
                  ? new Date(sub.next_billing_date).toLocaleDateString()
                  : "N/A"}
              </p>
            </div>
          </div>

          {sub.free_delivery && (
            <Badge className="bg-green-50 text-green-700">Free Delivery Included</Badge>
          )}

          {isPaused && sub.pause_until_date && (
            <p className="text-sm text-yellow-700 bg-yellow-50 p-3 rounded-lg">
              Paused until {new Date(sub.pause_until_date).toLocaleDateString()}
            </p>
          )}

          {/* Subscription Items */}
          {sub.items.length > 0 && (
            <div className="border-t pt-4">
              <p className="text-sm font-medium mb-2">Your Meals</p>
              <div className="space-y-2">
                {sub.items.map((item) => (
                  <div key={item.id} className="flex justify-between text-sm">
                    <span>{item.quantity}x {item.menu_item_name}</span>
                    <span className="text-gray-500">Week {item.week_number}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Manage Subscription</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {isActive && (
              <>
                <Button variant="outline" onClick={() => setPauseOpen(true)} disabled={actionLoading}>
                  <Pause className="h-4 w-4 mr-2" />
                  Pause Subscription
                </Button>
                <Button variant="outline" onClick={() => setSkipOpen(true)} disabled={actionLoading}>
                  <SkipForward className="h-4 w-4 mr-2" />
                  Skip a Week
                </Button>
              </>
            )}
            {isPaused && (
              <Button className="bg-green-600 hover:bg-green-700" onClick={handleResume} disabled={actionLoading}>
                <Play className="h-4 w-4 mr-2" />
                Resume Subscription
              </Button>
            )}
            {(isActive || isPaused) && (
              <Button variant="destructive" onClick={() => setCancelOpen(true)} disabled={actionLoading}>
                <X className="h-4 w-4 mr-2" />
                Cancel Subscription
              </Button>
            )}
          </div>

          {sub.skipped_weeks.length > 0 && (
            <div className="mt-4 pt-4 border-t">
              <p className="text-sm font-medium mb-2">Skipped Weeks</p>
              <div className="flex flex-wrap gap-2">
                {sub.skipped_weeks.map((week) => (
                  <Badge key={week} variant="secondary">
                    {new Date(week).toLocaleDateString()}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pause Dialog */}
      <Dialog open={pauseOpen} onOpenChange={setPauseOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Pause Subscription</DialogTitle>
            <DialogDescription>
              Choose a date to resume your subscription. You won&apos;t be billed during the pause.
            </DialogDescription>
          </DialogHeader>
          <div>
            <Label htmlFor="pauseDate">Resume Date</Label>
            <Input
              id="pauseDate"
              type="date"
              value={pauseDate}
              onChange={(e) => setPauseDate(e.target.value)}
              min={minPauseDate}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setPauseOpen(false)}>Cancel</Button>
            <Button onClick={handlePause} disabled={!pauseDate || actionLoading}>
              Pause
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Skip Week Dialog */}
      <Dialog open={skipOpen} onOpenChange={setSkipOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Skip a Week</DialogTitle>
            <DialogDescription>
              Choose a delivery date to skip. You won&apos;t receive or be charged for that week.
            </DialogDescription>
          </DialogHeader>
          <div>
            <Label htmlFor="skipDate">Week to Skip</Label>
            <Input
              id="skipDate"
              type="date"
              value={skipDate}
              onChange={(e) => setSkipDate(e.target.value)}
              min={minSkipDate}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setSkipOpen(false)}>Cancel</Button>
            <Button onClick={handleSkip} disabled={!skipDate || actionLoading}>
              Skip Week
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Cancel Dialog */}
      <Dialog open={cancelOpen} onOpenChange={setCancelOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancel Subscription</DialogTitle>
            <DialogDescription>
              Are you sure? You&apos;ll lose your subscription benefits including free delivery and discounts.
            </DialogDescription>
          </DialogHeader>
          <div>
            <Label htmlFor="cancelReason">Reason (optional)</Label>
            <Input
              id="cancelReason"
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
              placeholder="Tell us why you're leaving..."
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCancelOpen(false)}>Keep Subscription</Button>
            <Button variant="destructive" onClick={handleCancel} disabled={actionLoading}>
              Confirm Cancellation
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
