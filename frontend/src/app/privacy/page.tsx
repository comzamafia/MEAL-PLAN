import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy | Wela Meal Plan",
  description: "Privacy Policy for Wela Meal Plan - How we collect, use, and protect your personal information.",
};

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container max-w-4xl mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold mb-8">Privacy Policy</h1>
        <p className="text-gray-600 mb-8">Last updated: March 2026</p>

        <div className="prose prose-gray max-w-none space-y-8">
          <section>
            <h2 className="text-2xl font-semibold mb-4">Introduction</h2>
            <p>
              Wela Meal Plan (&ldquo;we&rdquo;, &ldquo;our&rdquo;, or &ldquo;us&rdquo;) is committed to protecting your privacy.
              This Privacy Policy explains how we collect, use, disclose, and safeguard your
              information when you use our website and services, in compliance with the
              Personal Information Protection and Electronic Documents Act (PIPEDA).
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Information We Collect</h2>

            <h3 className="text-xl font-medium mt-4 mb-2">Personal Information</h3>
            <p>We collect information you provide directly to us:</p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li><strong>Account Information:</strong> Name, email address, phone number, password</li>
              <li><strong>Delivery Information:</strong> Street address, unit number, city, postal code, delivery instructions</li>
              <li><strong>Payment Information:</strong> Credit card details (processed securely by Stripe - we do not store full card numbers)</li>
              <li><strong>Order History:</strong> Items ordered, delivery dates, preferences</li>
              <li><strong>Communication Preferences:</strong> Marketing opt-in status, language preference</li>
            </ul>

            <h3 className="text-xl font-medium mt-4 mb-2">Automatically Collected Information</h3>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>IP address and browser type</li>
              <li>Device information</li>
              <li>Pages visited and time spent on our website</li>
              <li>Referral source</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">How We Use Your Information</h2>
            <p>We use the information we collect to:</p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>Process and fulfill your orders</li>
              <li>Communicate with you about orders, deliveries, and account updates</li>
              <li>Send promotional communications (only with your consent)</li>
              <li>Administer the Wela Points loyalty program</li>
              <li>Improve our website and services</li>
              <li>Prevent fraud and maintain security</li>
              <li>Comply with legal obligations</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Information Sharing</h2>
            <p>We share your information with:</p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li><strong>Stripe:</strong> For secure payment processing</li>
              <li><strong>Delivery Personnel:</strong> Name, address, and phone number for delivery</li>
              <li><strong>Email Service Provider (Postmark):</strong> For transactional and marketing emails</li>
              <li><strong>Analytics Providers:</strong> Aggregated, anonymized data for website improvement</li>
            </ul>
            <p className="mt-2">
              We do not sell your personal information to third parties.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Data Retention</h2>
            <p>
              We retain your personal information for as long as necessary to provide our
              services and fulfill the purposes outlined in this policy. Order history is
              retained for 7 years for tax and accounting purposes. You may request deletion
              of your account and personal data at any time.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Your Rights Under PIPEDA</h2>
            <p>You have the right to:</p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li><strong>Access:</strong> Request a copy of the personal information we hold about you</li>
              <li><strong>Correction:</strong> Request correction of inaccurate information</li>
              <li><strong>Deletion:</strong> Request deletion of your personal information</li>
              <li><strong>Withdraw Consent:</strong> Opt out of marketing communications at any time</li>
              <li><strong>Data Portability:</strong> Request your data in a portable format</li>
            </ul>
            <p className="mt-2">
              To exercise these rights, contact us at privacy@welamealprep.ca. We will
              respond to requests within 30 days.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Cookies and Tracking</h2>
            <p>
              We use cookies and similar technologies to improve your experience on our
              website. You can control cookies through your browser settings. For analytics
              and advertising, we use:
            </p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>Google Analytics 4 (for website analytics)</li>
              <li>Meta Pixel (for advertising, with your consent)</li>
            </ul>
            <p className="mt-2">
              Marketing cookies are only activated after you provide consent through our
              cookie banner.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Data Security</h2>
            <p>
              We implement appropriate technical and organizational measures to protect
              your personal information, including:
            </p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>SSL/TLS encryption for all data transmission</li>
              <li>PCI DSS compliant payment processing via Stripe</li>
              <li>Secure password hashing</li>
              <li>Regular security audits</li>
              <li>Access controls and employee training</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Children&apos;s Privacy</h2>
            <p>
              Our services are not directed to individuals under 18 years of age. We do
              not knowingly collect personal information from children.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Changes to This Policy</h2>
            <p>
              We may update this Privacy Policy from time to time. We will notify you of
              material changes by email or through a notice on our website.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Contact Us</h2>
            <p>
              If you have questions about this Privacy Policy or wish to exercise your
              privacy rights, contact our Privacy Officer:
            </p>
            <p className="mt-2">
              <strong>Email:</strong> privacy@welamealprep.ca<br />
              <strong>Address:</strong> Oakville, Ontario, Canada
            </p>
            <p className="mt-2">
              If you are not satisfied with our response, you may file a complaint with
              the Office of the Privacy Commissioner of Canada at{" "}
              <a href="https://www.priv.gc.ca" className="text-green-600 hover:underline">
                www.priv.gc.ca
              </a>.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
