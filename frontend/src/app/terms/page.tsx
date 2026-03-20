import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms of Service | Wela Meal Plan",
  description: "Terms of Service for Wela Meal Plan meal prep delivery service in Oakville and Halton Region.",
};

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container max-w-4xl mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold mb-8">Terms of Service</h1>
        <p className="text-gray-600 mb-8">Last updated: March 2026</p>

        <div className="prose prose-gray max-w-none space-y-8">
          <section>
            <h2 className="text-2xl font-semibold mb-4">1. Agreement to Terms</h2>
            <p>
              By accessing or using the Wela Meal Plan website and services (&ldquo;Services&rdquo;),
              you agree to be bound by these Terms of Service (&ldquo;Terms&rdquo;). If you do not
              agree to these Terms, please do not use our Services.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">2. Description of Services</h2>
            <p>
              Wela Meal Plan provides meal preparation and delivery services to customers
              in Oakville, Burlington, Milton, and surrounding areas in the Halton Region
              of Ontario, Canada. Our Services include:
            </p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>Weekly meal preparation and delivery</li>
              <li>Subscription meal plans</li>
              <li>One-time meal orders</li>
              <li>Wela Points loyalty program</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">3. Ordering and Payment</h2>
            <p>
              <strong>Order Cut-off:</strong> All orders must be placed by Friday at 5:00 PM EST
              for Sunday delivery.
            </p>
            <p className="mt-2">
              <strong>Payment:</strong> We accept major credit cards processed securely through
              Stripe. All prices are in Canadian Dollars (CAD) and include applicable taxes
              (HST) unless otherwise stated.
            </p>
            <p className="mt-2">
              <strong>Pricing:</strong> We reserve the right to change prices at any time.
              Subscription customers will be notified 7 days before any price changes take effect.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">4. Delivery</h2>
            <p>
              <strong>Delivery Area:</strong> We currently deliver to select postal codes in
              Oakville, Burlington, Milton, and Halton Region. Delivery availability is
              confirmed during checkout.
            </p>
            <p className="mt-2">
              <strong>Delivery Window:</strong> Deliveries are made on Sundays between
              3:00 PM and 5:00 PM. We cannot guarantee exact delivery times.
            </p>
            <p className="mt-2">
              <strong>Delivery Fees:</strong> Delivery fees vary by zone. Orders over $75
              qualify for free delivery.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">5. Food Safety</h2>
            <p>
              Our meals are prepared in a food-safe certified kitchen. Meals are delivered
              fresh (not frozen) and should be refrigerated immediately upon receipt.
              Meals remain fresh for up to 5 days when properly refrigerated at 4°C or below.
            </p>
            <p className="mt-2">
              <strong>Allergen Warning:</strong> Our kitchen handles common allergens
              including but not limited to peanuts, tree nuts, shellfish, dairy, eggs,
              wheat, and soy. While we take precautions, we cannot guarantee that our
              meals are free from allergen cross-contamination.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">6. Subscriptions</h2>
            <p>
              Subscription plans automatically renew based on your selected billing cycle
              (weekly, bi-weekly, or monthly). You may pause, skip, or cancel your
              subscription at any time through your account dashboard.
            </p>
            <p className="mt-2">
              <strong>Cancellation:</strong> Subscriptions must be cancelled before the
              weekly cut-off (Friday 5:00 PM) to avoid being charged for the following week.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">7. Wela Points Program</h2>
            <p>
              Customers earn 10 Wela Points per $1 spent. Points can be redeemed at a rate
              of 100 points = $1 discount. Points expire 12 months after earning.
              Points have no cash value and cannot be transferred.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">8. Limitation of Liability</h2>
            <p>
              To the maximum extent permitted by law, Wela Meal Plan shall not be liable
              for any indirect, incidental, special, consequential, or punitive damages
              resulting from your use of or inability to use the Services.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">9. Governing Law</h2>
            <p>
              These Terms shall be governed by and construed in accordance with the laws
              of the Province of Ontario and the federal laws of Canada applicable therein.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">10. Contact Us</h2>
            <p>
              If you have questions about these Terms, please contact us at:
            </p>
            <p className="mt-2">
              <strong>Email:</strong> hello@welamealprep.ca<br />
              <strong>Address:</strong> Oakville, Ontario, Canada
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
