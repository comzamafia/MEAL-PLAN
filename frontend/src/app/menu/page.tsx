"use client";

import { useEffect, useState, useRef, useMemo } from "react";
import { api, MenuItem } from "@/lib/api";
import { useCartStore } from "@/lib/store";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  ShoppingCart,
  Search,
  Flame,
  Leaf,
  Filter,
  Plus,
} from "lucide-react";
import Link from "next/link";
import Image from "next/image";

const spiceLabels = ["Mild", "Medium", "Spicy", "Very Spicy"];
const spiceColors = [
  "bg-green-100 text-green-700",
  "bg-yellow-100 text-yellow-700",
  "bg-orange-100 text-orange-700",
  "bg-red-100 text-red-700",
];

function MenuItemCard({ item }: { item: MenuItem }) {
  const addItem = useCartStore((s) => s.addItem);

  const handleAdd = () => {
    addItem({
      id: item.id,
      name_en: item.name_en,
      name_th: item.name_th,
      description_en: item.description_en,
      base_price: parseFloat(item.base_price),
      image_url: item.image_url,
      calories: item.calories,
      protein_g: item.protein_g,
      carbs_g: item.carbs_g,
      fat_g: item.fat_g,
      is_gluten_free: item.is_gluten_free,
      is_dairy_free: item.is_dairy_free,
      is_halal: item.is_halal,
      spice_level: item.spice_level,
    });
  };

  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
      <div className="aspect-[4/3] bg-gradient-to-br from-green-100 to-green-50 flex items-center justify-center">
        {item.image_url ? (
          <Image
            src={item.image_url}
            alt={item.name_en}
            width={400}
            height={300}
            className="w-full h-full object-cover"
            unoptimized
          />
        ) : (
          <span className="text-4xl">🍲</span>
        )}
      </div>
      <CardContent className="p-4 space-y-3">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-semibold text-gray-900">{item.name_en}</h3>
            {item.name_th && (
              <p className="text-xs text-gray-500">{item.name_th}</p>
            )}
          </div>
          <span className="text-lg font-bold text-green-700">
            ${parseFloat(item.base_price).toFixed(2)}
          </span>
        </div>

        <p className="text-sm text-gray-600 line-clamp-2">
          {item.description_en}
        </p>

        {/* Nutrition row */}
        <div className="flex gap-3 text-xs text-gray-500">
          <span>{item.calories} cal</span>
          <span>{item.protein_g}g protein</span>
          <span>{item.carbs_g}g carbs</span>
          <span>{item.fat_g}g fat</span>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-1.5">
          {item.spice_level > 0 && (
            <Badge className={`text-xs ${spiceColors[item.spice_level - 1]}`}>
              <Flame className="h-3 w-3 mr-0.5" />
              {spiceLabels[item.spice_level - 1]}
            </Badge>
          )}
          {item.is_gluten_free && (
            <Badge className="text-xs bg-emerald-100 text-emerald-700">GF</Badge>
          )}
          {item.is_dairy_free && (
            <Badge className="text-xs bg-blue-100 text-blue-700">DF</Badge>
          )}
          {item.is_halal && (
            <Badge className="text-xs bg-purple-100 text-purple-700">Halal</Badge>
          )}
        </div>

        <Button
          onClick={handleAdd}
          className="w-full bg-green-600 hover:bg-green-700"
          size="sm"
        >
          <Plus className="h-4 w-4 mr-1" />
          Add to Cart
        </Button>
      </CardContent>
    </Card>
  );
}

export default function MenuPage() {
  const [items, setItems] = useState<MenuItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");
  const [dietary, setDietary] = useState<string[]>([]);
  const didLoad = useRef(false);
  const totalItems = useCartStore((s) => s.getTotalItems());

  useEffect(() => {
    if (didLoad.current) return;
    didLoad.current = true;
    async function load() {
      const res = await api.getMenuItems();
      if (res.data) setItems(res.data);
      setLoading(false);
    }
    load();
  }, []);

  const categories = useMemo(() => {
    const cats = new Set(items.map((i) => i.category));
    return ["all", ...Array.from(cats)];
  }, [items]);

  const filtered = useMemo(() => {
    return items.filter((item) => {
      if (category !== "all" && item.category !== category) return false;
      if (search && !item.name_en.toLowerCase().includes(search.toLowerCase())) return false;
      if (dietary.includes("gluten_free") && !item.is_gluten_free) return false;
      if (dietary.includes("dairy_free") && !item.is_dairy_free) return false;
      if (dietary.includes("halal") && !item.is_halal) return false;
      return true;
    });
  }, [items, category, search, dietary]);

  const toggleDietary = (key: string) => {
    setDietary((prev) =>
      prev.includes(key) ? prev.filter((d) => d !== key) : [...prev, key]
    );
  };

  return (
    <>
      <Header />
      <main className="min-h-screen bg-gray-50">
        {/* Hero */}
        <section className="bg-gradient-to-r from-green-700 to-green-600 text-white py-12">
          <div className="container mx-auto px-4 text-center">
            <h1 className="text-3xl md:text-4xl font-bold">Our Menu</h1>
            <p className="mt-2 text-green-100 max-w-xl mx-auto">
              Authentic Thai meals, cooked fresh weekly. Browse our rotating selection and add your favourites to the cart.
            </p>
          </div>
        </section>

        <div className="container mx-auto px-4 py-8">
          {/* Filters */}
          <div className="flex flex-col md:flex-row gap-4 mb-8">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search meals..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
              />
            </div>

            <div className="flex flex-wrap gap-2 items-center">
              <Filter className="h-4 w-4 text-gray-500" />
              {categories.map((cat) => (
                <Button
                  key={cat}
                  variant={category === cat ? "default" : "outline"}
                  size="sm"
                  onClick={() => setCategory(cat)}
                  className={category === cat ? "bg-green-600 hover:bg-green-700" : ""}
                >
                  {cat === "all" ? "All" : cat}
                </Button>
              ))}
            </div>

            <div className="flex gap-2">
              <Button
                variant={dietary.includes("gluten_free") ? "default" : "outline"}
                size="sm"
                onClick={() => toggleDietary("gluten_free")}
                className={dietary.includes("gluten_free") ? "bg-emerald-600 hover:bg-emerald-700" : ""}
              >
                <Leaf className="h-3 w-3 mr-1" />
                GF
              </Button>
              <Button
                variant={dietary.includes("dairy_free") ? "default" : "outline"}
                size="sm"
                onClick={() => toggleDietary("dairy_free")}
                className={dietary.includes("dairy_free") ? "bg-blue-600 hover:bg-blue-700" : ""}
              >
                DF
              </Button>
              <Button
                variant={dietary.includes("halal") ? "default" : "outline"}
                size="sm"
                onClick={() => toggleDietary("halal")}
                className={dietary.includes("halal") ? "bg-purple-600 hover:bg-purple-700" : ""}
              >
                Halal
              </Button>
            </div>
          </div>

          {/* Results */}
          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
                <div key={i} className="h-80 bg-gray-200 rounded-xl animate-pulse" />
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <div className="text-center py-16 text-gray-500">
              <p className="text-lg">No meals match your filters</p>
              <Button
                variant="outline"
                className="mt-4"
                onClick={() => { setSearch(""); setCategory("all"); setDietary([]); }}
              >
                Clear Filters
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filtered.map((item) => (
                <MenuItemCard key={item.id} item={item} />
              ))}
            </div>
          )}
        </div>

        {/* Floating cart */}
        {totalItems > 0 && (
          <div className="fixed bottom-6 right-6 z-40">
            <Link href="/#checkout">
              <Button className="bg-green-600 hover:bg-green-700 shadow-xl rounded-full h-14 px-6 text-base">
                <ShoppingCart className="h-5 w-5 mr-2" />
                Cart ({totalItems})
              </Button>
            </Link>
          </div>
        )}
      </main>
      <Footer />
    </>
  );
}
