export function SchemaMarkup() {
  const localBusinessSchema = {
    "@context": "https://schema.org",
    "@type": "FoodEstablishment",
    "@id": "https://welamealprep.ca/#business",
    "name": "Wela Meal Plan",
    "alternateName": "Wela Meal Prep",
    "description": "Premium Thai-inspired meal prep delivered fresh to Oakville, Burlington, and Halton Region. High protein, macro-friendly meals made by Chef Dusit Thani trained chefs.",
    "url": "https://welamealprep.ca",
    "telephone": "",
    "email": "hello@welamealprep.ca",
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "Oakville",
      "addressRegion": "Ontario",
      "addressCountry": "CA"
    },
    "geo": {
      "@type": "GeoCoordinates",
      "latitude": 43.4675,
      "longitude": -79.6877
    },
    "areaServed": [
      {
        "@type": "City",
        "name": "Oakville",
        "containedInPlace": {
          "@type": "AdministrativeArea",
          "name": "Ontario"
        }
      },
      {
        "@type": "City",
        "name": "Burlington"
      },
      {
        "@type": "City",
        "name": "Milton"
      },
      {
        "@type": "City",
        "name": "Mississauga"
      }
    ],
    "servesCuisine": ["Thai", "Healthy", "Meal Prep"],
    "priceRange": "$$",
    "paymentAccepted": ["Credit Card"],
    "currenciesAccepted": "CAD",
    "openingHoursSpecification": [
      {
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "opens": "00:00",
        "closes": "23:59"
      }
    ],
    "hasOfferCatalog": {
      "@type": "OfferCatalog",
      "name": "Meal Prep Menu",
      "itemListElement": [
        {
          "@type": "Offer",
          "itemOffered": {
            "@type": "MenuItem",
            "name": "Thai Basil Chicken",
            "description": "Classic Thai basil chicken with jasmine rice"
          }
        },
        {
          "@type": "Offer",
          "itemOffered": {
            "@type": "MenuItem",
            "name": "Green Curry",
            "description": "Authentic Thai green curry with vegetables"
          }
        }
      ]
    },
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": "4.9",
      "reviewCount": "127",
      "bestRating": "5",
      "worstRating": "1"
    }
  };

  const organizationSchema = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "@id": "https://welamealprep.ca/#organization",
    "name": "Wela Meal Plan",
    "url": "https://welamealprep.ca",
    "logo": "https://welamealprep.ca/logo.png",
    "sameAs": [
      "https://instagram.com/welamealprep",
      "https://facebook.com/welamealprep"
    ],
    "contactPoint": {
      "@type": "ContactPoint",
      "email": "hello@welamealprep.ca",
      "contactType": "customer service",
      "availableLanguage": ["English", "Thai"]
    }
  };

  const websiteSchema = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "@id": "https://welamealprep.ca/#website",
    "url": "https://welamealprep.ca",
    "name": "Wela Meal Plan",
    "description": "Premium Thai-inspired meal prep delivery in Halton Region",
    "publisher": {
      "@id": "https://welamealprep.ca/#organization"
    }
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(localBusinessSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(websiteSchema) }}
      />
    </>
  );
}
