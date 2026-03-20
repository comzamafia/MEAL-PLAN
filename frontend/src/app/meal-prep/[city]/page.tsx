import { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";

// Supported cities for SEO
const cities = {
  oakville: {
    name: "Oakville",
    region: "Halton Region",
    postalCodes: ["L6H", "L6J", "L6K", "L6L", "L6M"],
    description: "Premium Thai-inspired meal prep delivered fresh to Oakville every Sunday. High protein, macro-friendly meals made by trained chefs.",
    neighborhoods: ["Downtown Oakville", "Bronte", "Glen Abbey", "Joshua Creek", "Clearview", "Eastlake"],
  },
  burlington: {
    name: "Burlington",
    region: "Halton Region",
    postalCodes: ["L7L", "L7M", "L7N", "L7P", "L7R", "L7S", "L7T"],
    description: "Fresh Thai-inspired meal prep delivery in Burlington. Healthy, high-protein meals delivered to your door every Sunday.",
    neighborhoods: ["Downtown Burlington", "Aldershot", "Tansley", "Palmer", "Millcroft", "Headon Forest"],
  },
  milton: {
    name: "Milton",
    region: "Halton Region",
    postalCodes: ["L9T", "L9E"],
    description: "Convenient meal prep delivery in Milton. Thai-inspired, macro-friendly meals prepared fresh and delivered weekly.",
    neighborhoods: ["Old Milton", "Beaty", "Timberlea", "Scott", "Harrison", "Clarke"],
  },
  mississauga: {
    name: "Mississauga",
    region: "Peel Region",
    postalCodes: ["L4W", "L4X", "L4Y", "L4Z", "L5A", "L5B", "L5C", "L5E", "L5G", "L5H", "L5J", "L5K", "L5L", "L5M", "L5N", "L5R", "L5V", "L5W"],
    description: "Meal prep delivery available in select Mississauga areas. Fresh Thai-inspired meals delivered every Sunday.",
    neighborhoods: ["Port Credit", "Lorne Park", "Clarkson", "Streetsville", "Meadowvale", "Erin Mills"],
  },
};

type CityKey = keyof typeof cities;

interface PageProps {
  params: Promise<{ city: string }>;
}

export async function generateStaticParams() {
  return Object.keys(cities).map((city) => ({
    city,
  }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { city } = await params;
  const cityData = cities[city as CityKey];

  if (!cityData) {
    return {
      title: "City Not Found | Wela Meal Plan",
    };
  }

  return {
    title: `Meal Prep Delivery in ${cityData.name} | Wela Meal Plan`,
    description: cityData.description,
    keywords: [
      `meal prep ${cityData.name}`,
      `meal delivery ${cityData.name}`,
      `healthy meals ${cityData.name}`,
      `Thai food ${cityData.name}`,
      `macro meal prep ${cityData.region}`,
    ],
    openGraph: {
      title: `Meal Prep Delivery in ${cityData.name} | Wela Meal Plan`,
      description: cityData.description,
      url: `https://welamealprep.ca/meal-prep/${city}`,
      siteName: "Wela Meal Plan",
      locale: "en_CA",
      type: "website",
    },
  };
}

export default async function CityPage({ params }: PageProps) {
  const { city } = await params;
  const cityData = cities[city as CityKey];

  if (!cityData) {
    notFound();
  }

  const citySchema = {
    "@context": "https://schema.org",
    "@type": "Service",
    "name": `Meal Prep Delivery in ${cityData.name}`,
    "description": cityData.description,
    "provider": {
      "@type": "LocalBusiness",
      "name": "Wela Meal Plan",
      "url": "https://welamealprep.ca"
    },
    "areaServed": {
      "@type": "City",
      "name": cityData.name,
      "containedInPlace": {
        "@type": "AdministrativeArea",
        "name": cityData.region
      }
    },
    "serviceType": "Meal Prep Delivery"
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Schema Markup */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(citySchema) }}
      />

      {/* Hero Section */}
      <section className="bg-gradient-to-b from-green-50 to-white py-16 md:py-24">
        <div className="container px-4 md:px-6">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl mb-6">
              Meal Prep Delivery in {cityData.name}
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              {cityData.description}
            </p>
            <Button asChild size="lg" className="bg-green-600 hover:bg-green-700">
              <Link href="/#order">Order Now - Free Delivery</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Service Areas */}
      <section className="py-16">
        <div className="container px-4 md:px-6">
          <h2 className="text-2xl font-bold text-center mb-8">
            We Deliver to All {cityData.name} Neighborhoods
          </h2>
          <div className="max-w-2xl mx-auto">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {cityData.neighborhoods.map((neighborhood) => (
                <div
                  key={neighborhood}
                  className="bg-white p-4 rounded-lg border text-center"
                >
                  <span className="text-gray-700">{neighborhood}</span>
                </div>
              ))}
            </div>
            <p className="text-center text-gray-500 mt-6 text-sm">
              Serving postal codes: {cityData.postalCodes.join(", ")}
            </p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16 bg-white">
        <div className="container px-4 md:px-6">
          <h2 className="text-2xl font-bold text-center mb-12">
            How Meal Prep Delivery Works in {cityData.name}
          </h2>
          <div className="grid md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">1</span>
              </div>
              <h3 className="font-semibold mb-2">Order by Wednesday</h3>
              <p className="text-sm text-gray-600">
                Choose your meals online before our weekly cutoff
              </p>
            </div>
            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">2</span>
              </div>
              <h3 className="font-semibold mb-2">We Cook Saturday</h3>
              <p className="text-sm text-gray-600">
                Fresh meals prepared with premium ingredients
              </p>
            </div>
            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">3</span>
              </div>
              <h3 className="font-semibold mb-2">Sunday Delivery</h3>
              <p className="text-sm text-gray-600">
                Delivered to your {cityData.name} address 3-5 PM
              </p>
            </div>
            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">4</span>
              </div>
              <h3 className="font-semibold mb-2">Heat & Enjoy</h3>
              <p className="text-sm text-gray-600">
                Ready in 3 minutes, fresh for 5 days
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Why Choose Us */}
      <section className="py-16">
        <div className="container px-4 md:px-6">
          <h2 className="text-2xl font-bold text-center mb-12">
            Why {cityData.name} Residents Choose Wela
          </h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="bg-white p-6 rounded-lg border">
              <h3 className="font-semibold mb-2">Free Local Delivery</h3>
              <p className="text-sm text-gray-600">
                Free delivery on all orders to {cityData.name}. No minimum order required.
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg border">
              <h3 className="font-semibold mb-2">Fresh, Never Frozen</h3>
              <p className="text-sm text-gray-600">
                Meals are cooked fresh on Saturday and delivered Sunday.
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg border">
              <h3 className="font-semibold mb-2">High Protein Meals</h3>
              <p className="text-sm text-gray-600">
                30-45g protein per meal. Perfect for fitness goals.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-green-600 text-white">
        <div className="container px-4 md:px-6 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Try Meal Prep in {cityData.name}?
          </h2>
          <p className="text-lg mb-8 opacity-90">
            Join hundreds of {cityData.name} families who save time with Wela.
          </p>
          <Button asChild size="lg" variant="secondary">
            <Link href="/#order">View This Week&apos;s Menu</Link>
          </Button>
        </div>
      </section>

      {/* Other Cities */}
      <section className="py-16 bg-white">
        <div className="container px-4 md:px-6">
          <h2 className="text-xl font-semibold text-center mb-6">
            We Also Deliver To
          </h2>
          <div className="flex flex-wrap justify-center gap-4">
            {Object.entries(cities)
              .filter(([key]) => key !== city)
              .map(([key, data]) => (
                <Link
                  key={key}
                  href={`/meal-prep/${key}`}
                  className="text-green-600 hover:underline"
                >
                  {data.name}
                </Link>
              ))}
          </div>
        </div>
      </section>
    </div>
  );
}
