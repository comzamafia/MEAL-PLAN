"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { api, SavedAddress } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { MapPin, Plus, Pencil, Trash2, Star } from "lucide-react";

const emptyAddress = {
  label: "",
  recipient_name: "",
  phone: "",
  street_address: "",
  unit: "",
  city: "",
  province: "ON",
  postal_code: "",
  country: "CA",
  delivery_instructions: "",
};

export default function AddressesPage() {
  const [addresses, setAddresses] = useState<SavedAddress[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState(emptyAddress);
  const [saving, setSaving] = useState(false);
  const didLoad = useRef(false);

  const loadAddresses = useCallback(async () => {
    const res = await api.getAddresses();
    if (res.data) setAddresses(res.data);
    setLoading(false);
  }, []);

  useEffect(() => {
    if (didLoad.current) return;
    didLoad.current = true;
    // eslint-disable-next-line react-hooks/set-state-in-effect -- Initial data fetch from API
    loadAddresses();
  }, [loadAddresses]);

  const openNew = () => {
    setEditingId(null);
    setForm(emptyAddress);
    setDialogOpen(true);
  };

  const openEdit = (addr: SavedAddress) => {
    setEditingId(addr.id);
    setForm({
      label: addr.label,
      recipient_name: addr.recipient_name,
      phone: addr.phone,
      street_address: addr.street_address,
      unit: addr.unit,
      city: addr.city,
      province: addr.province,
      postal_code: addr.postal_code,
      country: addr.country,
      delivery_instructions: addr.delivery_instructions,
    });
    setDialogOpen(true);
  };

  const handleSave = async () => {
    setSaving(true);
    if (editingId) {
      await api.updateAddress(editingId, form);
    } else {
      await api.createAddress(form);
    }
    setDialogOpen(false);
    await loadAddresses();
    setSaving(false);
  };

  const handleDelete = async (id: string) => {
    await api.deleteAddress(id);
    await loadAddresses();
  };

  const handleSetDefault = async (id: string) => {
    await api.setDefaultAddress(id);
    await loadAddresses();
  };

  const updateField = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 bg-gray-200 rounded animate-pulse" />
        {[1, 2].map((i) => (
          <div key={i} className="h-28 bg-gray-200 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Delivery Addresses</h1>
          <p className="text-gray-500 mt-1">Manage your saved delivery addresses.</p>
        </div>
        <Button onClick={openNew} className="bg-green-600 hover:bg-green-700">
          <Plus className="h-4 w-4 mr-2" />
          Add Address
        </Button>
      </div>

      {addresses.length === 0 ? (
        <Card>
          <CardContent className="pt-6 text-center py-12">
            <MapPin className="h-10 w-10 text-gray-300 mx-auto mb-3" />
            <p className="font-medium text-gray-700">No addresses saved</p>
            <p className="text-sm text-gray-500 mt-1">
              Add a delivery address for faster checkout.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {addresses.map((addr) => (
            <Card key={addr.id}>
              <CardContent className="pt-5">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="font-medium">{addr.label || "Address"}</p>
                      {addr.is_default && (
                        <Badge className="bg-green-100 text-green-700 text-xs">Default</Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{addr.recipient_name}</p>
                    <p className="text-sm text-gray-500">
                      {addr.street_address}
                      {addr.unit && `, Unit ${addr.unit}`}
                    </p>
                    <p className="text-sm text-gray-500">
                      {addr.city}, {addr.province} {addr.postal_code}
                    </p>
                    {addr.phone && (
                      <p className="text-sm text-gray-400 mt-1">{addr.phone}</p>
                    )}
                    {addr.delivery_instructions && (
                      <p className="text-xs text-gray-400 mt-1 italic">
                        {addr.delivery_instructions}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-1">
                    {!addr.is_default && (
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={() => handleSetDefault(addr.id)}
                        title="Set as default"
                      >
                        <Star className="h-4 w-4" />
                      </Button>
                    )}
                    <Button variant="ghost" size="icon-sm" onClick={() => openEdit(addr)}>
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      onClick={() => handleDelete(addr.id)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add/Edit Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{editingId ? "Edit Address" : "Add Address"}</DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>Label</Label>
                <Input
                  placeholder="Home, Work..."
                  value={form.label}
                  onChange={(e) => updateField("label", e.target.value)}
                />
              </div>
              <div>
                <Label>Recipient Name</Label>
                <Input
                  value={form.recipient_name}
                  onChange={(e) => updateField("recipient_name", e.target.value)}
                  required
                />
              </div>
            </div>
            <div>
              <Label>Phone</Label>
              <Input
                type="tel"
                value={form.phone}
                onChange={(e) => updateField("phone", e.target.value)}
              />
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div className="col-span-2">
                <Label>Street Address</Label>
                <Input
                  value={form.street_address}
                  onChange={(e) => updateField("street_address", e.target.value)}
                  required
                />
              </div>
              <div>
                <Label>Unit</Label>
                <Input
                  value={form.unit}
                  onChange={(e) => updateField("unit", e.target.value)}
                  placeholder="Apt, Suite..."
                />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <Label>City</Label>
                <Input
                  value={form.city}
                  onChange={(e) => updateField("city", e.target.value)}
                  required
                />
              </div>
              <div>
                <Label>Province</Label>
                <Input
                  value={form.province}
                  onChange={(e) => updateField("province", e.target.value)}
                  required
                />
              </div>
              <div>
                <Label>Postal Code</Label>
                <Input
                  value={form.postal_code}
                  onChange={(e) => updateField("postal_code", e.target.value)}
                  placeholder="L6H 1A1"
                  required
                />
              </div>
            </div>
            <div>
              <Label>Delivery Instructions</Label>
              <Input
                value={form.delivery_instructions}
                onChange={(e) => updateField("delivery_instructions", e.target.value)}
                placeholder="Ring doorbell, leave at side door..."
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleSave} disabled={saving} className="bg-green-600 hover:bg-green-700">
              {saving ? "Saving..." : editingId ? "Update" : "Add Address"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
