import type { Metadata } from "next";
import { Poppins, Sarabun } from "next/font/google";
import "./globals.css";
import { SchemaMarkup } from "@/components/seo/schema-markup";
import { CookieConsent } from "@/components/marketing/cookie-consent";

const poppins = Poppins({
  variable: "--font-poppins",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

const sarabun = Sarabun({
  variable: "--font-sarabun",
  subsets: ["thai", "latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Wela Meal Plan | Healthy Meal Prep Delivery in Oakville",
  description:
    "Premium Thai-inspired meal prep delivered fresh to your door in Oakville, Burlington, and Halton Region. High protein, macro-friendly meals made by Chef Dusit Thani trained chefs.",
  keywords: [
    "meal prep Oakville",
    "healthy meal delivery",
    "Thai meal prep",
    "macro friendly meals",
    "Halton Region meal delivery",
    "high protein meals",
  ],
  openGraph: {
    title: "Wela Meal Plan | Healthy Meal Prep Delivery in Oakville",
    description:
      "Premium Thai-inspired meal prep delivered fresh to your door. High protein, macro-friendly meals.",
    url: "https://welamealprep.ca",
    siteName: "Wela Meal Plan",
    locale: "en_CA",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Wela Meal Plan | Healthy Meal Prep Delivery",
    description: "Premium Thai-inspired meal prep delivered fresh to your door.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${poppins.variable} ${sarabun.variable} scroll-smooth`}
    >
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <meta name="theme-color" content="#16a34a" />
      </head>
      <body className="min-h-screen bg-background font-sans antialiased">
        <SchemaMarkup />
        {children}
        <CookieConsent />
      </body>
    </html>
  );
}
