"use client";

import { useState } from "react";
import { useAuthStore } from "@/lib/auth-store";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Settings, Check } from "lucide-react";

export default function SettingsPage() {
  const { user, setUser } = useAuthStore();
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const [language, setLanguage] = useState(user?.preferred_language ?? "en");
  const [emailOptIn, setEmailOptIn] = useState(user?.email_marketing_opt_in ?? false);
  const [smsOptIn, setSmsOptIn] = useState(user?.sms_opt_in ?? false);
  const [dietaryNotes, setDietaryNotes] = useState(user?.dietary_notes ?? "");

  const handleSave = async () => {
    setSaving(true);
    const res = await api.updateProfile({
      preferred_language: language,
      email_marketing_opt_in: emailOptIn,
      sms_opt_in: smsOptIn,
      dietary_notes: dietaryNotes,
    });
    if (res.status === "success" && res.data) {
      setUser(res.data);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    }
    setSaving(false);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Account Settings</h1>

      {/* Profile Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Profile Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-gray-500">Name</Label>
              <p className="font-medium">
                {user?.user.first_name} {user?.user.last_name}
              </p>
            </div>
            <div>
              <Label className="text-gray-500">Email</Label>
              <p className="font-medium">{user?.user.email}</p>
            </div>
            <div>
              <Label className="text-gray-500">Phone</Label>
              <p className="font-medium">{user?.user.phone || "Not set"}</p>
            </div>
            <div>
              <Label className="text-gray-500">Member Since</Label>
              <p className="font-medium">
                {user?.user.created_at
                  ? new Date(user.user.created_at).toLocaleDateString("en-CA", {
                      year: "numeric",
                      month: "long",
                    })
                  : "N/A"}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Preferences */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Settings className="h-4 w-4" />
            Preferences
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-5">
          {/* Language */}
          <div>
            <Label>Language</Label>
            <div className="flex gap-2 mt-1.5">
              <Button
                variant={language === "en" ? "default" : "outline"}
                size="sm"
                onClick={() => setLanguage("en")}
                className={language === "en" ? "bg-green-600 hover:bg-green-700" : ""}
              >
                English
              </Button>
              <Button
                variant={language === "th" ? "default" : "outline"}
                size="sm"
                onClick={() => setLanguage("th")}
                className={language === "th" ? "bg-green-600 hover:bg-green-700" : ""}
              >
                ไทย
              </Button>
            </div>
          </div>

          {/* Dietary Notes */}
          <div>
            <Label htmlFor="dietaryNotes">Dietary Notes & Allergies</Label>
            <Input
              id="dietaryNotes"
              value={dietaryNotes}
              onChange={(e) => setDietaryNotes(e.target.value)}
              placeholder="e.g., No peanuts, low sodium preferred..."
              className="mt-1.5"
            />
          </div>

          {/* Communication */}
          <div className="space-y-3">
            <Label>Communication Preferences</Label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={emailOptIn}
                onChange={(e) => setEmailOptIn(e.target.checked)}
                className="h-4 w-4 rounded"
              />
              <div>
                <p className="text-sm font-medium">Email Marketing</p>
                <p className="text-xs text-gray-500">
                  Receive promotions, new menu updates, and special offers by email
                </p>
              </div>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={smsOptIn}
                onChange={(e) => setSmsOptIn(e.target.checked)}
                className="h-4 w-4 rounded"
              />
              <div>
                <p className="text-sm font-medium">SMS Notifications</p>
                <p className="text-xs text-gray-500">
                  Get delivery updates and order confirmations via text
                </p>
              </div>
            </label>
          </div>

          <div className="flex items-center gap-3 pt-2">
            <Button
              onClick={handleSave}
              disabled={saving}
              className="bg-green-600 hover:bg-green-700"
            >
              {saving ? "Saving..." : "Save Preferences"}
            </Button>
            {saved && (
              <Badge className="bg-green-100 text-green-700">
                <Check className="h-3 w-3 mr-1" />
                Saved
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
