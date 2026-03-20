import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Refund & Cancellation Policy | Wela Meal Plan",
  description: "Refund and cancellation policy for Wela Meal Plan - Understanding our policies for orders and subscriptions.",
};

export default function RefundsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container max-w-4xl mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold mb-8">Refund & Cancellation Policy</h1>
        <p className="text-gray-600 mb-8">Last updated: March 2026</p>

        <div className="prose prose-gray max-w-none space-y-8">
          <section>
            <h2 className="text-2xl font-semibold mb-4">Order Cutoff Times</h2>
            <p>
              Understanding our weekly schedule is important for managing your orders:
            </p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li><strong>Order Deadline:</strong> Wednesday 11:59 PM EST for Sunday delivery</li>
              <li><strong>Preparation Day:</strong> Saturday (meals are cooked fresh)</li>
              <li><strong>Delivery Day:</strong> Sunday between 3:00 PM - 5:00 PM</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">One-Time Order Cancellations</h2>

            <h3 className="text-xl font-medium mt-4 mb-2">Before Wednesday 11:59 PM</h3>
            <p>
              Orders can be cancelled for a <strong>full refund</strong> at any time before the
              weekly cutoff. Simply contact us or cancel through your account dashboard.
            </p>

            <h3 className="text-xl font-medium mt-4 mb-2">After Wednesday 11:59 PM</h3>
            <p>
              Once we begin meal preparation on Saturday, orders <strong>cannot be cancelled
              or refunded</strong> as ingredients have already been purchased and meals are
              being prepared specifically for your order.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Subscription Management</h2>

            <h3 className="text-xl font-medium mt-4 mb-2">Pausing Your Subscription</h3>
            <p>
              You can pause your subscription at any time before the Wednesday cutoff.
              Paused subscriptions will not be charged or receive deliveries until resumed.
              There is no limit to how long you can keep your subscription paused.
            </p>

            <h3 className="text-xl font-medium mt-4 mb-2">Skipping a Week</h3>
            <p>
              Need to skip just one delivery? You can skip up to 4 consecutive weeks
              without affecting your subscription status. Skip requests must be made
              before Wednesday 11:59 PM for the upcoming Sunday delivery.
            </p>

            <h3 className="text-xl font-medium mt-4 mb-2">Cancelling Your Subscription</h3>
            <p>
              You may cancel your subscription at any time. If cancelled before the
              Wednesday cutoff, no further charges will occur. If cancelled after the
              cutoff, your final delivery will still be fulfilled and charged as scheduled.
            </p>
            <p className="mt-2">
              <strong>Note:</strong> Cancelling your subscription does not affect any
              accumulated Wela Points - they remain in your account for future use.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Refund Eligibility</h2>

            <h3 className="text-xl font-medium mt-4 mb-2">Full Refund</h3>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>Order cancelled before Wednesday 11:59 PM cutoff</li>
              <li>Delivery not received (and confirmed by our records)</li>
              <li>Significant quality issues reported within 24 hours of delivery</li>
              <li>Wrong meals delivered</li>
            </ul>

            <h3 className="text-xl font-medium mt-4 mb-2">Partial Refund or Credit</h3>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>Missing items from your order (refund for missing items only)</li>
              <li>Minor quality concerns (store credit for future orders)</li>
            </ul>

            <h3 className="text-xl font-medium mt-4 mb-2">No Refund</h3>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>Change of mind after Wednesday cutoff</li>
              <li>Not home during delivery window (re-delivery fee may apply)</li>
              <li>Issues reported more than 24 hours after delivery</li>
              <li>Personal taste preferences</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Quality Guarantee</h2>
            <p>
              We take pride in our food quality. If you receive meals that don&apos;t meet
              our standards, please:
            </p>
            <ol className="list-decimal pl-6 mt-2 space-y-1">
              <li>Take photos of the issue</li>
              <li>Contact us within 24 hours of delivery</li>
              <li>Provide your order number and description of the issue</li>
            </ol>
            <p className="mt-2">
              We will review your case and provide a refund or credit within 3 business days.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Wela Points Refunds</h2>
            <p>
              When an order is refunded:
            </p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>Points earned from that order will be deducted from your balance</li>
              <li>Points redeemed on that order will be returned to your account</li>
              <li>Referral bonuses tied to refunded orders may be reversed</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Coupon & Discount Refunds</h2>
            <p>
              For orders placed with coupons or discounts:
            </p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>Refunds are calculated based on the actual amount paid</li>
              <li>One-time use coupons may not be restored after a refund</li>
              <li>First-order discounts cannot be reapplied to future orders</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Refund Processing</h2>
            <p>
              Approved refunds are processed as follows:
            </p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li><strong>Credit Card:</strong> 5-10 business days to appear on your statement</li>
              <li><strong>Store Credit:</strong> Applied immediately to your account</li>
              <li><strong>Wela Points:</strong> Restored within 24 hours</li>
            </ul>
            <p className="mt-2">
              Please note that your bank may take additional time to process the refund.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Delivery Issues</h2>

            <h3 className="text-xl font-medium mt-4 mb-2">Missed Delivery</h3>
            <p>
              If you are not home during the delivery window (3:00 PM - 5:00 PM), our
              driver will leave the package in a safe location or follow your delivery
              instructions. We are not responsible for spoilage if meals are left outside
              for extended periods.
            </p>

            <h3 className="text-xl font-medium mt-4 mb-2">Failed Delivery Attempts</h3>
            <p>
              If delivery cannot be completed (e.g., inaccessible location, wrong address),
              we will contact you to arrange re-delivery. A $5 re-delivery fee may apply.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Contact Us</h2>
            <p>
              For refund requests or questions about this policy:
            </p>
            <p className="mt-2">
              <strong>Email:</strong> support@welamealprep.ca<br />
              <strong>Response Time:</strong> Within 24 hours on business days
            </p>
            <p className="mt-4 text-sm text-gray-500">
              This policy is subject to change. Material changes will be communicated
              via email to active subscribers.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
