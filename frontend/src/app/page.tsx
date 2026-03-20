import { Header } from "@/components/layout/header";
import { Hero } from "@/components/sections/hero";
import { Benefits } from "@/components/sections/benefits";
import { MenuPreview } from "@/components/sections/menu-preview";
import { HowItWorks } from "@/components/sections/how-it-works";
import { Testimonials } from "@/components/sections/testimonials";
import { CheckoutSection } from "@/components/sections/checkout-section";
import { Footer } from "@/components/layout/footer";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />

      <main className="flex-1">
        {/* Hero Section */}
        <Hero />

        {/* Benefits Grid */}
        <Benefits />

        {/* Menu Preview */}
        <MenuPreview />

        {/* How It Works */}
        <HowItWorks />

        {/* Testimonials */}
        <Testimonials />

        {/* 2-Step Checkout Section */}
        <CheckoutSection />
      </main>

      <Footer />
    </div>
  );
}
