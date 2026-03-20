"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useCartStore, MenuItem } from "@/lib/store";

// Sample menu data (will be fetched from API in production)
const sampleMenu: MenuItem[] = [
  {
    id: "1",
    name_en: "Basil Chicken with Brown Rice",
    name_th: "ข้าวกะเพราไก่",
    description_en: "Stir-fried minced chicken with holy basil, garlic, and chilies. Served with jasmine brown rice and a fried egg.",
    base_price: 13.99,
    calories: 520,
    protein_g: 45,
    carbs_g: 42,
    fat_g: 18,
    is_gluten_free: true,
    is_dairy_free: true,
    is_halal: true,
    spice_level: 2,
  },
  {
    id: "2",
    name_en: "Lemongrass Grilled Chicken",
    name_th: "ไก่ย่างตะไคร้",
    description_en: "Tender chicken breast marinated in lemongrass and Thai herbs. Served with quinoa and steamed vegetables.",
    base_price: 14.99,
    calories: 480,
    protein_g: 48,
    carbs_g: 35,
    fat_g: 14,
    is_gluten_free: true,
    is_dairy_free: true,
    is_halal: true,
    spice_level: 1,
  },
  {
    id: "3",
    name_en: "Thai Beef Salad",
    name_th: "ยำเนื้อ",
    description_en: "Grilled beef strips with fresh herbs, cucumber, tomatoes in a spicy lime dressing.",
    base_price: 15.99,
    calories: 420,
    protein_g: 42,
    carbs_g: 18,
    fat_g: 22,
    is_gluten_free: true,
    is_dairy_free: true,
    is_halal: true,
    spice_level: 3,
  },
  {
    id: "4",
    name_en: "Coconut Curry Salmon",
    name_th: "แกงกะหรี่แซลมอน",
    description_en: "Pan-seared salmon in a light coconut curry sauce. Served with fragrant jasmine rice.",
    base_price: 16.99,
    calories: 550,
    protein_g: 40,
    carbs_g: 38,
    fat_g: 26,
    is_gluten_free: true,
    is_dairy_free: false,
    is_halal: true,
    spice_level: 1,
  },
];

export function MenuPreview() {
  const addItem = useCartStore((state) => state.addItem);

  return (
    <section id="menu" className="py-16 md:py-24 bg-gray-50">
      <div className="container px-4 md:px-6">
        <div className="text-center mb-12">
          <Badge variant="secondary" className="mb-4">
            This Week&apos;s Menu
          </Badge>
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
            Fresh Meals, Ready to Heat
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Our menu rotates weekly to keep things exciting. Order by Friday for
            Sunday delivery.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {sampleMenu.map((item) => (
            <Card
              key={item.id}
              className="overflow-hidden hover:shadow-lg transition-shadow"
            >
              <div className="aspect-video bg-gradient-to-br from-green-100 to-green-200 relative">
                <div className="absolute inset-0 flex items-center justify-center text-4xl">
                  🍱
                </div>
                {item.spice_level > 0 && (
                  <Badge
                    variant="secondary"
                    className="absolute top-2 right-2 bg-red-100 text-red-800"
                  >
                    {"🌶️".repeat(item.spice_level)}
                  </Badge>
                )}
              </div>
              <CardContent className="p-4">
                <h3 className="font-semibold text-lg mb-1">{item.name_en}</h3>
                <p className="text-sm text-gray-500 mb-3 line-clamp-2">
                  {item.description_en}
                </p>

                {/* Nutrition Info */}
                <div className="flex gap-2 mb-3 flex-wrap">
                  <Badge variant="outline" className="text-xs">
                    {item.calories} cal
                  </Badge>
                  <Badge variant="outline" className="text-xs bg-green-50">
                    {item.protein_g}g protein
                  </Badge>
                </div>

                {/* Dietary Badges */}
                <div className="flex gap-1 mb-4 flex-wrap">
                  {item.is_gluten_free && (
                    <Badge variant="secondary" className="text-xs">
                      GF
                    </Badge>
                  )}
                  {item.is_dairy_free && (
                    <Badge variant="secondary" className="text-xs">
                      DF
                    </Badge>
                  )}
                  {item.is_halal && (
                    <Badge variant="secondary" className="text-xs">
                      Halal
                    </Badge>
                  )}
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-lg font-bold text-green-600">
                    ${item.base_price.toFixed(2)}
                  </span>
                  <Button
                    size="sm"
                    className="bg-green-600 hover:bg-green-700"
                    onClick={() => addItem(item)}
                  >
                    Add to Cart
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="text-center mt-8">
          <Button variant="outline" size="lg">
            View Full Menu
          </Button>
        </div>
      </div>
    </section>
  );
}
