# Wela Meal Plan — Web Application Project Specification

> **Version:** 2.0  
> **Stack:** Next.js 14+ (App Router) · Django 5+ (DRF) · PostgreSQL · Stripe · Vercel / Railway  
> **Market:** Oakville / Halton Region, Ontario, Canada  
> **Updated:** June 2025

---

## Table of Contents

1. [Phase 1 — Project Setup & Architecture](#phase-1)
2. [Phase 2 — Database Design](#phase-2)
3. [Phase 3 — Backend API Development](#phase-3)
4. [Phase 4 — Frontend (Funnel Pages)](#phase-4)
5. [Phase 5 — Marketing Tech & SEO](#phase-5)
6. [Phase 6 — Operations & Admin System](#phase-6)
7. [Phase 7 — Notification System ⚠️ NEW](#phase-7)
8. [Phase 8 — Security, Compliance & Legal ⚠️ NEW](#phase-8)
9. [Phase 9 — Payment Edge Cases & Stripe Webhooks ⚠️ NEW](#phase-9)
10. [Phase 10 — Testing Strategy ⚠️ NEW](#phase-10)
11. [Phase 11 — DevOps & CI/CD Pipeline ⚠️ NEW](#phase-11)
12. [Phase 12 — Performance & Caching ⚠️ NEW](#phase-12)
13. [Phase 13 — Error Monitoring & Observability ⚠️ NEW](#phase-13)
14. [Phase 14 — Tax, Finance & Canadian Compliance ⚠️ NEW](#phase-14)
15. [Gap Analysis Summary](#gap-analysis)

---

## Phase 1 — Project Setup & Architecture {#phase-1}

### 1.1 Frontend (Next.js 14+ App Router)
- [ ] Initialize Next.js project with TypeScript and Tailwind CSS
- [ ] Configure State Management (Zustand) for Cart and Checkout Flow
- [ ] Configure Stripe.js for client-side payment rendering
- [ ] Set up `next-intl` for bilingual support (EN / TH) — needed because `name_th` and `name_en` fields exist in the data model
- [ ] Configure `next/image` with CDN domain allowlist for menu item images

### 1.2 Backend (Django 5+ & Django Rest Framework)
- [ ] Initialize Django project and configure PostgreSQL database
- [ ] Configure CORS with strict origin whitelist (frontend domain only)
- [ ] Configure Authentication — JWT via `djangorestframework-simplejwt`
- [ ] Install and configure Stripe Python SDK
- [ ] Set up `django-storages` + AWS S3 (or Cloudflare R2) for media file storage
- [ ] Configure `django-redis` as cache backend

### 1.3 Infrastructure & Deployment
- [ ] Provision hosting — Vercel for Next.js, Railway (or Render) for Django
- [ ] Register and connect domain (e.g., `welamealprep.ca`)
- [ ] Provision SSL certificate — automatic via Vercel/Railway, verify TLS 1.2+
- [ ] Provision **Redis** instance — Railway Redis or Upstash (required for caching and Celery)
- [ ] Provision **AWS S3** bucket (or Cloudflare R2) for menu images, with a CDN in front
- [ ] Set up **Sentry** projects (one for Next.js, one for Django) before first deploy
- [ ] Set up **environment tiers**: `development`, `staging`, `production`
- [ ] Store all secrets in environment variables — never commit `.env` to Git; use Vercel/Railway secret manager

---

## Phase 2 — Database Design (Django Models) {#phase-2}

### 2.1 User & Authentication Models
- [ ] Extend Custom User model with Role field (`customer`, `admin`, `kitchen_staff`, `driver`)
- [ ] `CustomerProfile`: delivery addresses (multiple), Wela Points balance, referral code, preferred language (EN/TH), communication preferences (email, SMS)
- [ ] `DeliveryAddress`: supports multiple saved addresses per customer (label, street, city, province, postal_code, is_default)

### 2.2 Product & Menu Models
- [ ] `Category`: main categories (The Perfect Box, The Lean Grill, Bulk Protein)
- [ ] `MenuItem`: full menu item model
  - **Core:** `name_th`, `name_en`, `description_th`, `description_en`, `base_price`, `image_url` (S3/CDN path)
  - **Nutrition (per box):** `calories`, `protein_g`, `carbs_g`, `fat_g`, `fiber_g`, `sodium_mg`, `sugar_g`
  - **Safety:** `ingredients_list`, `allergens` (JSON array), `is_gluten_free`, `is_dairy_free`, `is_halal`, `spice_level` (0–3)
  - **Consumption:** `heating_instructions_th`, `heating_instructions_en`, `storage_instructions`, `shelf_life_days`
  - **Management:** `is_active`, `rotation_week` (1–4), `available_from_date`, `available_until_date`
- [ ] `MenuModifier`: add-on options per menu item (brown rice swap +$0, boiled egg +$1.50), includes `modifier_name`, `price_delta`, `is_available`
- [ ] `RecipeComponent`: links `MenuItem` to raw ingredients for Food Cost calculation and automatic stock deduction
- [ ] `Ingredient`: raw ingredient master (name, unit, current_stock_qty, reorder_threshold, cost_per_unit, supplier)

### 2.3 Order & Subscription Models
- [ ] `Order`: order ID, customer FK, total amount, subtotal, discount, tax (GST/HST), delivery date, delivery window, status (`pending`, `confirmed`, `prep`, `out_for_delivery`, `delivered`, `cancelled`, `refunded`), stripe_payment_intent_id
- [ ] `OrderItem`: FK to Order and MenuItem, quantity, unit_price, modifiers snapshot (JSON — store snapshot at time of order, not live FK, to preserve history)
- [ ] `Subscription`: customer FK, status (`active`, `paused`, `cancelled`, `past_due`), plan type, billing cycle, next_billing_date, stripe_subscription_id, stripe_customer_id, pause_until_date, cancellation_reason
- [ ] `SubscriptionItem`: items included in the subscription plan week

### 2.4 Marketing & Loyalty Models
- [ ] `Coupon`: code, discount type (`percent`, `fixed`), discount_value, max_uses, current_uses, min_order_amount, expiry_date, is_first_order_only, is_active
- [ ] `LoyaltyPoint`: customer FK, points_delta (+/-), reason, order FK (nullable), created_at — full ledger history
- [ ] `ReferralHistory`: referrer, referred_user, reward_issued (Boolean), reward_issued_at, order FK (qualifying order)

### 2.5 Delivery & Route Models ⚠️ NEW
- [ ] `DeliveryZone`: postal code prefix, label (e.g., "Oakville North"), is_active, delivery_fee, free_delivery_threshold
- [ ] `DeliveryWindow`: date, time_start, time_end, max_orders, current_orders (for capacity management), is_open
- [ ] `DriverAssignment`: order FK, driver user FK, assigned_at, picked_up_at, delivered_at, driver_notes

---

## Phase 3 — Backend API Development (DRF) {#phase-3}

### 3.1 Menu API
- [ ] `GET /api/menu/` — returns menu items for the current rotation week with Macros; supports query params: `?category=`, `?is_gluten_free=`, `?max_calories=`, `?min_protein=`, `?allergen_exclude=`
- [ ] `GET /api/menu/{id}/` — single item detail including full ingredient list and allergen breakdown

### 3.2 Checkout API
- [ ] `POST /api/checkout/create-intent/` — creates Stripe PaymentIntent or SetupIntent; returns `client_secret`
- [ ] `POST /api/checkout/confirm/` — called after frontend payment confirmation; creates Order and OrderItems in DB
- [ ] `POST /api/checkout/order-bump/` — adds bump item to an in-progress order before payment confirmation

### 3.3 Upsell (OTO) API
- [ ] `POST /api/checkout/oto/` — 1-click charge using saved Stripe payment method to upgrade order to subscription; requires prior SetupIntent completion

### 3.4 Coupon & Loyalty API
- [ ] `POST /api/coupons/validate/` — validates coupon code, returns discount amount and updated cart total
- [ ] `GET /api/loyalty/balance/` — returns authenticated user's current Wela Points balance and transaction history
- [ ] `POST /api/loyalty/redeem/` — applies Wela Points to an active checkout (with points-to-dollar conversion rule)

### 3.5 Subscription Management API ⚠️ NEW
- [ ] `POST /api/subscriptions/pause/` — pauses active subscription until a specified date
- [ ] `POST /api/subscriptions/resume/` — resumes a paused subscription
- [ ] `POST /api/subscriptions/cancel/` — cancels subscription (triggers Stripe cancellation + records reason)
- [ ] `POST /api/subscriptions/skip-week/` — marks next delivery as skipped without cancelling

### 3.6 Referral API ⚠️ NEW
- [ ] `GET /api/referral/link/` — returns or generates the authenticated customer's unique referral URL
- [ ] `POST /api/referral/apply/` — validates and applies a referral code during checkout for new users

### 3.7 Kitchen Operations API
- [ ] `GET /api/kitchen/prep-list/` — authenticated kitchen staff only; returns aggregated quantities per menu item for a given delivery date
- [ ] `GET /api/kitchen/procurement/` — returns raw ingredient purchase summary after cut-off, with quantities broken down by dish
- [ ] `GET /api/kitchen/recipe-matrix/` — full Standard Recipe Matrix with ingredient proportions per item and per batch size

### 3.8 Delivery API ⚠️ NEW
- [ ] `GET /api/delivery/zones/` — returns list of active delivery zones and fees (used for postal code validation at checkout)
- [ ] `POST /api/delivery/validate-postal/` — validates a postal code against serviceable zones; returns zone, delivery fee, and next available delivery window
- [ ] `GET /api/delivery/route-export/` — authenticated admin only; exports delivery order list optimized for routing (address, customer name, items, delivery window)

### 3.9 Webhook API ⚠️ NEW
- [ ] `POST /api/webhooks/stripe/` — receives all Stripe events; must verify `Stripe-Signature` header with webhook secret before processing (see Phase 9)

### 3.10 API Standards ⚠️ NEW
- [ ] All authenticated endpoints require JWT Bearer token
- [ ] All endpoints return consistent JSON envelope: `{ "status": "success"|"error", "data": {}, "message": "" }`
- [ ] Implement API versioning prefix `/api/v1/`
- [ ] Generate OpenAPI 3.0 schema via `drf-spectacular` and serve Swagger UI at `/api/docs/` (restrict to non-production)
- [ ] Apply per-IP rate limiting via `django-ratelimit` — stricter limits on auth and checkout endpoints

---

## Phase 4 — Frontend Development (DotCom Secrets Funnel) {#phase-4}

### 4.1 Page 1 — Landing Page (`/`)
- [ ] **Hero Section:** Campaign headline "The Oakville Weekday Rescue Kit" + primary CTA button
- [ ] **Story & Trust Section:** Chef Dusit Thani standard badge, full Nutrition Facts table (macros + micronutrients), customer testimonials
- [ ] **2-Step Checkout Component:**
  - Step 1: Delivery form with real-time postal code validation against `/api/delivery/validate-postal/`; show delivery fee and next window immediately
  - Step 2: Stripe Elements embed, real-time coupon code field, Wela Points toggle, GST/HST line item display before final total
- [ ] **Order Bump Element:** highlighted add-on box for "Bulk Basil Chicken Breast 300g" shown between Step 2 form and Pay button
- [ ] **Trust Badges:** SSL lock icon, Stripe Verified Partner badge, "Local Oakville Kitchen" label

### 4.2 Page 2 — OTO Upsell Page (`/oto`)
- [ ] Display subscription upgrade offer — free delivery lock-in + free weekly snack
- [ ] "Yes, Upgrade My Order" button triggers 1-click charge via `/api/checkout/oto/` — show clear loading and success states
- [ ] "No thanks, I'll pay full price next time" link — clear, not hidden; leads to Thank You page
- [ ] Countdown timer (optional urgency element — must be honest about expiry)

### 4.3 Page 3 — Thank You & Referral Page (`/thank-you`)
- [ ] Order summary card (items, delivery window: Sunday 15:00–17:00)
- [ ] Wela Points earned display
- [ ] Unique referral link with one-click copy and pre-filled social share cards (Facebook, LINE, WhatsApp)
- [ ] Heating and storage instruction reminder card

### 4.4 Customer Dashboard (`/dashboard`)
- [ ] Subscription control panel: Pause, Resume, Skip Week, Cancel — all with confirmation modals
- [ ] Order history table with per-order nutrition totals (cumulative macros)
- [ ] Wela Points ledger (balance + earn/spend history)
- [ ] Saved delivery addresses management (add, edit, set default)
- [ ] Preference settings: communication language (EN/TH), email/SMS opt-in
- [ ] Active coupon / promo codes display

### 4.5 Legal Pages ⚠️ NEW
- [ ] `/terms` — Terms of Service (EN)
- [ ] `/privacy` — Privacy Policy (EN) — must comply with PIPEDA (see Phase 8)
- [ ] `/refunds` — Refund & Cancellation Policy
- [ ] `/allergens` — Allergen Information & Food Safety Statement
- [ ] All legal pages linked in footer; must be accessible before checkout

---

## Phase 5 — Marketing Tech & SEO {#phase-5}

### 5.1 Server-Side Tracking
- [ ] Install Meta Conversions API (CAPI) — send `Purchase`, `InitiateCheckout`, `AddToCart` events server-side to bypass browser blocking
- [ ] Install Google Analytics 4 (GA4) server-side via Measurement Protocol
- [ ] Set up Google Tag Manager (server-side container) on a subdomain (e.g., `gtm.welamealprep.ca`)
- [ ] Implement cookie consent banner compliant with CASL (Canadian Anti-Spam Legislation) before firing any tracking pixels client-side

### 5.2 Local SEO — Oakville Focused
- [ ] Create dynamic routes `/meal-prep/[city]` for city-level keyword targeting (Oakville, Burlington, Mississauga, Milton)
- [ ] Embed `LocalBusiness` + `Restaurant` Schema Markup in `layout.tsx` with `areaServed` specifying Halton Region postal codes
- [ ] Meta tags and image `alt` text geo-targeted to Oakville (e.g., "healthy meal prep delivery Oakville Ontario")
- [ ] Submit to Google Business Profile with accurate service area
- [ ] Create `/sitemap.xml` (auto-generated via `next-sitemap`) and submit to Google Search Console

### 5.3 Content SEO ⚠️ NEW
- [ ] Static blog section `/blog` for recipe posts, nutrition guides, and local lifestyle content — boosts organic traffic
- [ ] FAQ page `/faq` with FAQ Schema Markup — targets featured snippet positions for "meal prep Oakville" type queries
- [ ] Optimize Core Web Vitals (LCP < 2.5s, CLS < 0.1, INP < 200ms) — required for Google ranking 2025+

---

## Phase 6 — Operations & Admin System {#phase-6}

### 6.1 Admin Dashboard (Django Admin + Custom React Views)
- [ ] Configure Django Admin with role-based access (admin sees all; kitchen staff sees prep/recipe views only; driver sees delivery views only)
- [ ] **Cut-off Time Management:** configurable cut-off date/time per delivery window; auto-closes order intake and triggers kitchen notification
- [ ] **Menu Rotation Scheduler:** admin sets which menu items are active for each rotation week; changes take effect automatically at the scheduled start of each week
- [ ] **Prep List Report:** printable/exportable PDF showing aggregated quantities per dish for a delivery date
- [ ] **Standard Recipe Matrix:** shows ingredient weights and proportions per batch size, exportable to Excel
- [ ] **Procurement Summary:** aggregates all raw ingredient needs post-cut-off; exportable to `.csv` for supplier ordering

### 6.2 Delivery Operations ⚠️ NEW
- [ ] **Delivery Route Export:** generates ordered stop list for each driver, sorted by route optimization (either manual zone grouping or integration with Google Maps Directions API)
- [ ] **Driver Assignment View:** admin assigns orders to drivers; drivers see their list on a simple mobile-friendly view
- [ ] **Delivery Status Tracking:** driver marks orders as `picked_up` and `delivered` via a simple mobile web interface (no native app required initially)
- [ ] **Cut-off Zone Management:** admin can open/close specific delivery zones per week

### 6.3 Inventory & Stock Management ⚠️ NEW
- [ ] **Stock Dashboard:** current quantity on hand vs. reorder threshold per raw ingredient
- [ ] **Auto-deduction:** when an order is confirmed, `RecipeComponent` quantities are deducted from `Ingredient` stock
- [ ] **Low Stock Alert:** sends email to admin when any ingredient falls below `reorder_threshold`
- [ ] **Waste Tracking:** admin can log ingredient waste/spoilage to keep stock counts accurate

---

## Phase 7 — Notification System ⚠️ NEW {#phase-7}

This entire phase was absent from the original spec. A meal prep subscription business depends heavily on automated transactional communication.

### 7.1 Email Provider Setup
- [ ] Integrate **Postmark** (or SendGrid) as the transactional email provider
- [ ] Configure a dedicated sending domain (e.g., `mail.welamealprep.ca`) with SPF, DKIM, and DMARC DNS records
- [ ] Create HTML email templates (branded, mobile-responsive) for each email type below
- [ ] Store all email content bilingual (EN/TH) — render based on customer's `preferred_language`

### 7.2 Transactional Emails (Automated Triggers)
- [ ] **Order Confirmation** — sent immediately on `order.status = confirmed`; includes items, delivery window, heating instructions
- [ ] **Subscription Activated** — sent when subscription goes `active`; includes billing cycle, next delivery date, dashboard link
- [ ] **Subscription Payment Reminder** — sent 3 days before next billing date
- [ ] **Subscription Payment Failed** — sent when Stripe `invoice.payment_failed` webhook fires; includes payment retry link
- [ ] **Subscription Renewal Successful** — sent after successful recurring charge; includes delivery schedule
- [ ] **Subscription Paused Confirmation** — sent when customer pauses; includes resume date and how to change it
- [ ] **Subscription Cancellation Confirmation** — sent on cancellation; includes win-back offer (e.g., 15% off if they resubscribe within 30 days)
- [ ] **Delivery Dispatched** — sent Sunday morning when orders are picked up; includes estimated delivery window
- [ ] **Delivery Completed** — sent after driver marks order delivered; includes satisfaction survey link
- [ ] **Low Stock / Skip Notice** — sent if a menu item runs out and an order must be substituted; requires admin approval before sending
- [ ] **Referral Reward Earned** — sent when a referred user completes their first qualifying order
- [ ] **Wela Points Earned** — sent after each order confirming points balance
- [ ] **Welcome Email** — sent on first account creation

### 7.3 SMS Notifications (Optional Phase 1, Required Phase 2)
- [ ] Integrate **Twilio** (or Vonage) for SMS
- [ ] Send SMS for: Delivery Dispatched, Delivery Completed (with delivery photo confirmation link)
- [ ] Customer must opt-in at checkout; opt-out must be supported via reply STOP

### 7.4 Internal / Operational Notifications
- [ ] **Admin — New Order Alert** — Slack webhook (or email) when an order is placed
- [ ] **Admin — Cut-off Reached** — notification when delivery intake closes, with total order count
- [ ] **Admin — Low Ingredient Stock** — email alert (see Phase 6.3)
- [ ] **Kitchen Staff — Prep List Ready** — email to kitchen team after cut-off with link to prep list

---

## Phase 8 — Security, Compliance & Legal ⚠️ NEW {#phase-8}

This is a critical phase for a Canadian business handling payment data and personal health (nutrition) data.

### 8.1 PIPEDA Compliance (Canadian Privacy Law)
- [ ] Publish a Privacy Policy that discloses: what personal data is collected, why, how long it is retained, whether it is shared with third parties (Stripe, Meta, Google), and how users can request deletion
- [ ] Implement **data deletion endpoint** — customers can request account and data deletion from the dashboard; must be completed within 30 days
- [ ] Implement **data export endpoint** — customers can download all their personal data (PIPEDA right of access)
- [ ] Only collect data that is necessary (data minimisation principle)
- [ ] Log all data processing activities in a Record of Processing Activities (ROPA) document (internal)

### 8.2 CASL Compliance (Canadian Anti-Spam Legislation)
- [ ] Obtain explicit opt-in consent for marketing emails at checkout — separate checkbox, pre-unchecked
- [ ] Every marketing email must include an unsubscribe link that works within 10 business days
- [ ] Transactional emails (order confirmations, subscription alerts) do not require opt-in but must not include marketing content
- [ ] Store consent timestamp and source for all email subscriptions

### 8.3 PCI DSS Compliance
- [ ] Never store raw card numbers, CVV, or full PANs on Wela servers — Stripe handles this via Stripe Elements / Stripe.js tokenization
- [ ] Use Stripe's hosted fields to minimize PCI DSS scope (SAQ A level)
- [ ] Confirm Stripe webhook signatures on every incoming event (see Phase 9)
- [ ] Restrict access to Stripe dashboard to admin accounts only with 2FA enabled

### 8.4 Application Security
- [ ] Enable Django's CSRF protection on all non-API views
- [ ] Set security headers on all responses: `Content-Security-Policy`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security`
- [ ] Validate and sanitize all user inputs server-side (never trust client-side validation alone)
- [ ] Apply per-endpoint rate limiting — especially on `/api/auth/`, `/api/coupons/validate/`, and `/api/checkout/`
- [ ] Implement account lockout after 5 failed login attempts (15-minute cooldown)
- [ ] Store passwords with Argon2 hashing (Django's strongest built-in option)
- [ ] Rotate JWT signing keys periodically; keep access token TTL short (15 minutes), refresh token longer (7 days)
- [ ] Set up **IP allowlisting** for Django Admin (`/admin/` route) — accessible only from office/VPN IPs in production
- [ ] Conduct a dependency audit (`pip-audit`, `npm audit`) before launch and schedule quarterly audits
- [ ] Configure S3 bucket as **private** — serve all media via signed URLs or CloudFront, never expose the raw S3 URL

### 8.5 Accessibility (WCAG 2.1 AA)
- [ ] All images must have descriptive `alt` text
- [ ] All form inputs must have associated `<label>` elements
- [ ] Colour contrast ratio ≥ 4.5:1 for all body text
- [ ] Keyboard navigation must work through the full checkout flow
- [ ] Run automated accessibility audit with `axe-core` as part of CI pipeline

---

## Phase 9 — Payment Edge Cases & Stripe Webhooks ⚠️ NEW {#phase-9}

The original spec mentions Stripe but does not detail webhook handling, which is essential for subscription reliability.

### 9.1 Stripe Webhook Events to Handle

| Stripe Event | Action Required |
|---|---|
| `payment_intent.succeeded` | Mark Order as `confirmed`, trigger order confirmation email |
| `payment_intent.payment_failed` | Mark Order as `failed`, notify customer to retry |
| `invoice.payment_succeeded` | Mark Subscription renewal as paid, send renewal confirmation email |
| `invoice.payment_failed` | Set Subscription to `past_due`, send payment failure email with retry link, start dunning sequence |
| `invoice.payment_action_required` | Send 3D Secure authentication email to customer |
| `customer.subscription.updated` | Sync subscription status changes from Stripe to local DB |
| `customer.subscription.deleted` | Set Subscription to `cancelled` in local DB |
| `customer.subscription.trial_will_end` | Send reminder email 3 days before trial ends |
| `charge.dispute.created` | Alert admin immediately via email + Slack; freeze associated order |
| `charge.refunded` | Mark Order as `refunded`, update customer Wela Points if applicable |

### 9.2 Webhook Implementation Requirements
- [ ] All webhook events must be verified using `stripe.Webhook.construct_event()` with the endpoint's signing secret — reject any event that fails signature verification
- [ ] Webhook handler must be **idempotent** — use Stripe's `event.id` to prevent double-processing if Stripe retries a failed delivery
- [ ] Store received webhook events in a `StripeWebhookEvent` model (`event_id`, `event_type`, `processed_at`, `payload`) for debugging
- [ ] Return `200 OK` immediately and process events asynchronously via Celery background tasks
- [ ] Set up a **Celery + Redis** task queue for all async processing (webhook handling, email sending, stock deduction)

### 9.3 Dunning Management
- [ ] On first failed payment: retry automatically after 3 days (Stripe Smart Retries handles this)
- [ ] After 3 failed retries: set subscription to `past_due`, send "Action Required" email with update payment link
- [ ] After 7 days past due: send final warning; after 14 days, auto-cancel subscription and send win-back offer

### 9.4 Refund Flow
- [ ] Admin can initiate full or partial refunds from the Admin dashboard — triggers Stripe refund API
- [ ] On refund: deduct corresponding Wela Points earned from that order
- [ ] If refund is issued after delivery, require admin to record a reason (spoilage, wrong item, customer complaint)
- [ ] Refund confirmation email sent to customer automatically

---

## Phase 10 — Testing Strategy ⚠️ NEW {#phase-10}

### 10.1 Frontend Testing
- [ ] **Unit Tests** — `Jest` + `React Testing Library` for all UI components, custom hooks, and utility functions
- [ ] **Integration Tests** — test full checkout flow with Stripe test mode cards
- [ ] **End-to-End Tests** — `Playwright` covering critical paths:
  - Visitor → add to cart → fill delivery form → enter payment → view thank-you page
  - Customer → login → dashboard → pause subscription → receive confirmation
  - Invalid postal code → see error message → cannot proceed to payment
- [ ] **Accessibility Tests** — `@axe-core/playwright` runs against all key pages in E2E suite
- [ ] Target: 80%+ coverage on business-critical components

### 10.2 Backend Testing
- [ ] **Unit Tests** — `pytest` + `pytest-django` for all model methods, serializers, and utility functions
- [ ] **API Integration Tests** — test every DRF endpoint with authenticated and unauthenticated requests, valid and invalid payloads
- [ ] **Stripe Webhook Tests** — use `stripe-mock` to simulate all webhook events listed in Phase 9
- [ ] **Celery Task Tests** — test all async tasks (email sending, stock deduction) in isolation with mocked services
- [ ] Target: 85%+ coverage on API and business logic layer

### 10.3 Test Environments
- [ ] Use Stripe **test mode** in development and staging — never use real card numbers in non-production
- [ ] Use separate Stripe webhook endpoints per environment (Stripe Dashboard → Webhooks → add endpoint per env)
- [ ] Use separate PostMark/SendGrid test streams in staging to prevent real emails being sent during testing
- [ ] Seed a realistic dataset (menu items, sample orders, customers) for staging environment

---

## Phase 11 — DevOps & CI/CD Pipeline ⚠️ NEW {#phase-11}

### 11.1 Version Control & Branching
- [ ] Use GitHub with branch protection on `main` — no direct pushes; all changes via Pull Requests
- [ ] Branch naming convention: `feature/`, `fix/`, `chore/`
- [ ] Require at least one code review approval before merging to `main`
- [ ] Require all CI checks to pass before merge

### 11.2 CI/CD with GitHub Actions

**On Pull Request:**
- [ ] Run `npm run lint` + `npm run test` (frontend)
- [ ] Run `pytest` + `flake8` (backend)
- [ ] Run `pip-audit` and `npm audit` for dependency vulnerabilities
- [ ] Run Playwright E2E tests against a preview deploy (Vercel preview URL)

**On Merge to `main` → Staging Deploy:**
- [ ] Auto-deploy frontend to Vercel staging environment
- [ ] Auto-deploy backend to Railway staging environment
- [ ] Run database migrations automatically
- [ ] Run smoke tests against staging

**On Release Tag → Production Deploy:**
- [ ] Promote staging build to production (no rebuild from source)
- [ ] Create GitHub Release with auto-generated changelog
- [ ] Send deployment notification to Slack

### 11.3 Environment Configuration
- [ ] Maintain separate `.env` files for each tier — never committed to Git
- [ ] Required environment variables documented in `.env.example` (committed)
- [ ] All secrets stored in Vercel/Railway environment variable manager
- [ ] Separate Stripe API keys per environment (test vs. live)
- [ ] Separate Meta CAPI tokens, GA4 measurement IDs per environment

### 11.4 Database Migration Safety
- [ ] All schema changes via Django migrations — never manual SQL in production
- [ ] Test migrations on staging with production data snapshot before running in production
- [ ] Back up the PostgreSQL database before every production deployment

---

## Phase 12 — Performance & Caching ⚠️ NEW {#phase-12}

### 12.1 Next.js Rendering Strategy
- [ ] **Static Generation (SSG):** Landing page `/`, legal pages `/terms`, `/privacy`, `/refunds`, `/allergens`, `/faq` — rebuild on CMS/content change
- [ ] **Incremental Static Regeneration (ISR):** Menu pages — revalidate every hour to reflect rotation changes without full rebuild
- [ ] **Server-Side Rendering (SSR):** Customer Dashboard `/dashboard` — user-specific data, cannot be cached at CDN level
- [ ] **Client-Side Rendering:** Checkout step 2 (Stripe Elements), real-time coupon validation

### 12.2 Django API Caching
- [ ] Cache `GET /api/menu/` response in Redis — TTL 1 hour; invalidate cache on any `MenuItem` save signal
- [ ] Cache `GET /api/delivery/zones/` in Redis — TTL 24 hours; invalidate when admin updates zones
- [ ] Do NOT cache any authenticated user-specific endpoints
- [ ] Enable Django's `select_related` and `prefetch_related` on all queryset-heavy endpoints to prevent N+1 queries

### 12.3 Image Performance
- [ ] All menu item images stored in S3/R2, served through CDN (CloudFront or Cloudflare)
- [ ] Provide images in WebP format with JPEG fallback
- [ ] Use `next/image` with `sizes` prop for responsive image loading
- [ ] Images should be pre-processed to multiple sizes on upload (thumbnail, card, full) using `Pillow` in Django

### 12.4 Database Performance
- [ ] Add indexes on: `Order.delivery_date`, `Order.status`, `Order.customer`, `Subscription.next_billing_date`, `MenuItem.rotation_week`, `MenuItem.is_active`
- [ ] Use PostgreSQL `EXPLAIN ANALYZE` to audit slow queries before launch
- [ ] Set up `django-silk` (development only) for query profiling during development

---

## Phase 13 — Error Monitoring & Observability ⚠️ NEW {#phase-13}

### 13.1 Error Tracking
- [ ] **Sentry** — install `@sentry/nextjs` and `sentry-sdk` for Django
- [ ] Configure Sentry to capture all unhandled exceptions in both frontend and backend
- [ ] Set up Sentry performance monitoring — track P95 response times on critical API endpoints
- [ ] Configure Sentry alerts: notify Slack channel when error rate > 5 errors/minute or any new `Critical` issue

### 13.2 Uptime Monitoring
- [ ] Set up **Better Uptime** (or UptimeRobot) to check `welamealprep.ca` and the API health endpoint every 1 minute
- [ ] Create a `/api/health/` endpoint on Django that checks DB connectivity and Redis connectivity
- [ ] Configure PagerDuty (or SMS alert) for on-call notification if uptime check fails for > 3 consecutive minutes

### 13.3 Structured Logging
- [ ] Configure Django to output **structured JSON logs** (use `python-json-logger`)
- [ ] Log fields: `timestamp`, `level`, `request_id`, `user_id` (if authenticated), `endpoint`, `status_code`, `duration_ms`
- [ ] Ship logs to a log aggregation service (Railway's built-in, Papertrail, or Logtail)
- [ ] Implement `X-Request-ID` header — generated by the load balancer or Next.js middleware and passed through to Django for end-to-end request tracing

### 13.4 Business Metrics Dashboard ⚠️ NEW
- [ ] **Revenue Dashboard** — daily/weekly/monthly revenue, MRR (Monthly Recurring Revenue), ARR
- [ ] **Subscription Metrics** — active subscriptions, churn rate, pause rate, MoM growth
- [ ] **Order Metrics** — average order value, orders per delivery window, top-selling items, most used modifiers
- [ ] **Customer Metrics** — new vs. returning customer ratio, Wela Points redemption rate, referral conversion rate
- [ ] **Nutrition Insights** — most popular macros profile (e.g., "high protein" segment size)
- [ ] Implement as a custom Django Admin view or a simple internal React dashboard at `/admin/metrics/`

---

## Phase 14 — Tax, Finance & Canadian Compliance ⚠️ NEW {#phase-14}

### 14.1 Canadian Tax (GST/HST/PST)
- [ ] Determine tax status of meal prep products — in Canada, most **prepared food** is subject to GST/HST; confirm with an accountant
- [ ] Ontario HST rate: **13%** (5% GST + 8% PST) — apply to all taxable items for Oakville/Halton orders
- [ ] Display tax as a separate line item on checkout, order confirmation, and all invoices
- [ ] Store `tax_rate`, `tax_amount`, `tax_type` (`HST`) on the `Order` model
- [ ] Issue tax-compliant electronic invoices — invoices must show business name, GST/HST registration number, date, itemised amounts, and tax amounts
- [ ] Register for a **GST/HST business number** with the CRA before accepting the first payment

### 14.2 Financial Reporting Exports
- [ ] Export **monthly revenue report** as CSV/Excel: orders, revenue, tax collected, Stripe fees, net revenue
- [ ] Export **Wela Points liability report** monthly — outstanding unredeemed points represent a financial liability
- [ ] Export **Food Cost report** monthly — total ingredient cost vs. total revenue = gross margin
- [ ] These exports support bookkeeping in QuickBooks or Wave Accounting

### 14.3 Receipts & Invoicing
- [ ] Auto-generate a PDF receipt for every order — include all required fields for a valid Canadian receipt
- [ ] Store PDF receipts in S3 and link from customer's order history page in the dashboard
- [ ] Stripe also generates invoices for subscription renewals — ensure they include the GST/HST registration number by configuring Stripe Tax or the Stripe Invoice `footer` field

---

## Gap Analysis Summary {#gap-analysis}

The table below summarises all gaps found in the original spec and which Phase addresses them.

| Gap | Severity | Addressed In |
|---|---|---|
| No Notification System (emails, SMS) | 🔴 Critical | Phase 7 |
| No Stripe Webhook handling | 🔴 Critical | Phase 9 |
| No PIPEDA / CASL compliance plan | 🔴 Critical | Phase 8 |
| No Canadian Tax (GST/HST) handling | 🔴 Critical | Phase 14 |
| No Testing Strategy (unit, E2E) | 🔴 Critical | Phase 10 |
| No CI/CD Pipeline | 🟠 High | Phase 11 |
| No Error Monitoring (Sentry, uptime) | 🟠 High | Phase 13 |
| No Dunning / Failed Payment Flow | 🟠 High | Phase 9 |
| No Refund Flow | 🟠 High | Phase 9 |
| No Celery / Async Task Queue | 🟠 High | Phase 9 |
| No Caching Strategy (Redis, ISR) | 🟠 High | Phase 12 |
| No Security Headers / Rate Limiting | 🟠 High | Phase 8 |
| No Delivery Zone / Driver Model | 🟡 Medium | Phase 2 & 6 |
| No Subscription API (pause/skip/cancel) | 🟡 Medium | Phase 3 |
| No Legal Pages (Privacy, Terms, Refunds) | 🟡 Medium | Phase 4 & 8 |
| No i18n Strategy (EN/TH despite having `name_th`) | 🟡 Medium | Phase 1 & 4 |
| No Referral API endpoints | 🟡 Medium | Phase 3 |
| No OpenAPI / Swagger Documentation | 🟡 Medium | Phase 3 |
| No Image CDN Strategy | 🟡 Medium | Phase 12 |
| No Business Metrics Dashboard | 🟡 Medium | Phase 13 |
| No GST/HST Invoice PDF generation | 🟡 Medium | Phase 14 |
| No Inventory / Stock Deduction flow | 🟡 Medium | Phase 6 |
| No Accessibility (WCAG 2.1) plan | 🟡 Medium | Phase 8 |
| No Cookie Consent banner (CASL) | 🟡 Medium | Phase 5 |
| No FAQ / Blog content for SEO | 🟢 Low | Phase 5 |
| No Driver mobile interface | 🟢 Low | Phase 6 |
| No Waste Tracking for kitchen | 🟢 Low | Phase 6 |

---

## Recommended Build Order

Given the gaps above, here is the recommended phase execution order to minimise rework and avoid launching with critical compliance gaps:

```
Phase 1 (Setup) → Phase 2 (DB) → Phase 8 (Security + Legal pages)
  → Phase 14 (Tax setup — register GST/HST before first transaction)
    → Phase 3 (Backend APIs) + Phase 9 (Stripe Webhooks)
      → Phase 7 (Notifications — Celery + email templates)
        → Phase 4 (Frontend) → Phase 5 (SEO/Tracking)
          → Phase 10 (Testing) → Phase 11 (CI/CD)
            → Phase 12 (Performance) → Phase 13 (Monitoring)
              → Phase 6 (Admin & Ops)
```

**Do not go live without:** Phase 8 (PIPEDA), Phase 9 (Webhooks), Phase 14 (GST number), and Phase 7 (at minimum order confirmation emails).

---

*Last reviewed: June 2025. Review again before launch for any changes to Stripe APIs, Canadian tax regulations, or Next.js major versions.*
