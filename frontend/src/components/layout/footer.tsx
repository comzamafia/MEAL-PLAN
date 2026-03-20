import Link from "next/link";

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="container px-4 py-12 md:px-6">
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {/* Brand */}
          <div className="space-y-4">
            <Link href="/" className="flex items-center gap-2">
              <span className="text-2xl font-bold text-white">Wela</span>
              <span className="text-sm text-green-400">Meal Plan</span>
            </Link>
            <p className="text-sm text-gray-400">
              Premium Thai-inspired meal prep delivered fresh to Oakville,
              Burlington, and Halton Region every Sunday.
            </p>
            <div className="flex gap-4">
              <a
                href="https://instagram.com/welamealprep"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors"
                aria-label="Instagram"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12.315 2c2.43 0 2.784.013 3.808.06 1.064.049 1.791.218 2.427.465a4.902 4.902 0 011.772 1.153 4.902 4.902 0 011.153 1.772c.247.636.416 1.363.465 2.427.048 1.067.06 1.407.06 4.123v.08c0 2.643-.012 2.987-.06 4.043-.049 1.064-.218 1.791-.465 2.427a4.902 4.902 0 01-1.153 1.772 4.902 4.902 0 01-1.772 1.153c-.636.247-1.363.416-2.427.465-1.067.048-1.407.06-4.123.06h-.08c-2.643 0-2.987-.012-4.043-.06-1.064-.049-1.791-.218-2.427-.465a4.902 4.902 0 01-1.772-1.153 4.902 4.902 0 01-1.153-1.772c-.247-.636-.416-1.363-.465-2.427-.047-1.024-.06-1.379-.06-3.808v-.63c0-2.43.013-2.784.06-3.808.049-1.064.218-1.791.465-2.427a4.902 4.902 0 011.153-1.772A4.902 4.902 0 015.45 2.525c.636-.247 1.363-.416 2.427-.465C8.901 2.013 9.256 2 11.685 2h.63zm-.081 1.802h-.468c-2.456 0-2.784.011-3.807.058-.975.045-1.504.207-1.857.344-.467.182-.8.398-1.15.748-.35.35-.566.683-.748 1.15-.137.353-.3.882-.344 1.857-.047 1.023-.058 1.351-.058 3.807v.468c0 2.456.011 2.784.058 3.807.045.975.207 1.504.344 1.857.182.466.399.8.748 1.15.35.35.683.566 1.15.748.353.137.882.3 1.857.344 1.054.048 1.37.058 4.041.058h.08c2.597 0 2.917-.01 3.96-.058.976-.045 1.505-.207 1.858-.344.466-.182.8-.398 1.15-.748.35-.35.566-.683.748-1.15.137-.353.3-.882.344-1.857.048-1.055.058-1.37.058-4.041v-.08c0-2.597-.01-2.917-.058-3.96-.045-.976-.207-1.505-.344-1.858a3.097 3.097 0 00-.748-1.15 3.098 3.098 0 00-1.15-.748c-.353-.137-.882-.3-1.857-.344-1.023-.047-1.351-.058-3.807-.058zM12 6.865a5.135 5.135 0 110 10.27 5.135 5.135 0 010-10.27zm0 1.802a3.333 3.333 0 100 6.666 3.333 3.333 0 000-6.666zm5.338-3.205a1.2 1.2 0 110 2.4 1.2 1.2 0 010-2.4z" />
                </svg>
              </a>
              <a
                href="https://facebook.com/welamealprep"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors"
                aria-label="Facebook"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z" />
                </svg>
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
              Quick Links
            </h3>
            <ul className="space-y-2">
              <li>
                <Link href="/#menu" className="text-sm hover:text-white transition-colors">
                  This Week&apos;s Menu
                </Link>
              </li>
              <li>
                <Link href="/#how-it-works" className="text-sm hover:text-white transition-colors">
                  How It Works
                </Link>
              </li>
              <li>
                <Link href="/#testimonials" className="text-sm hover:text-white transition-colors">
                  Customer Reviews
                </Link>
              </li>
              <li>
                <Link href="/#order" className="text-sm hover:text-white transition-colors">
                  Order Now
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
              Legal
            </h3>
            <ul className="space-y-2">
              <li>
                <Link href="/terms" className="text-sm hover:text-white transition-colors">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-sm hover:text-white transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/refunds" className="text-sm hover:text-white transition-colors">
                  Refund Policy
                </Link>
              </li>
              <li>
                <Link href="/allergens" className="text-sm hover:text-white transition-colors">
                  Allergen Information
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
              Contact Us
            </h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a
                  href="mailto:hello@welamealprep.ca"
                  className="hover:text-white transition-colors"
                >
                  hello@welamealprep.ca
                </a>
              </li>
              <li className="text-gray-400">
                Oakville, Ontario, Canada
              </li>
              <li className="pt-2">
                <span className="text-gray-400">Delivery Areas:</span>
                <br />
                Oakville, Burlington, Milton, Mississauga
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-gray-400">
            &copy; {currentYear} Wela Meal Plan. All rights reserved.
          </p>
          <div className="flex items-center gap-4">
            <span className="text-xs text-gray-500">
              Secure payments by
            </span>
            <svg className="h-6 w-auto text-gray-400" viewBox="0 0 60 25" fill="currentColor">
              <path d="M59.64 14.28h-8.06c.19 1.93 1.6 2.55 3.2 2.55 1.64 0 2.96-.37 4.05-.95l.6 4.6c-1.27.65-3.2 1.2-5.64 1.2-5.85 0-8.64-3.53-8.64-9.02 0-5.27 2.78-9.35 8.2-9.35 5.2 0 7.13 3.78 7.13 8.08 0 .98-.07 2.04-.14 2.89h-6.7zm-3.2-4.02c0-1.54-.65-3.26-2.37-3.26-1.72 0-2.52 1.65-2.7 3.26h5.07zM39.12 3.74l-.26 2.07h-.05c-.9-1.58-2.6-2.45-4.54-2.45-4.56 0-7.93 4.02-7.93 9.44 0 3.9 2.1 7.28 6.08 7.28 1.93 0 3.8-.9 4.93-2.45h.05l-.26 2.07h4.99V3.74h-5.01zm-3.4 12.16c-1.93 0-2.96-1.58-2.96-3.87 0-2.66 1.16-4.63 3.08-4.63 1.86 0 2.96 1.58 2.96 3.94 0 2.66-1.16 4.56-3.08 4.56zM21.24 13.5c0-2.66 1.44-4.32 3.36-4.32.72 0 1.3.13 1.79.39l.7-5.06c-.65-.26-1.37-.39-2.14-.39-1.72 0-3.36.9-4.32 2.84h-.07l.26-2.52h-5.07v15.26h5.49V13.5zM12.76 2c-1.65 0-2.96 1.3-2.96 2.96 0 1.64 1.3 2.96 2.96 2.96 1.64 0 2.96-1.32 2.96-2.96 0-1.65-1.32-2.96-2.96-2.96zm2.78 17.7h-5.49V3.74h5.49V19.7zM4.18 9.88H0v9.82h4.18c2.9 0 4.88-2.07 4.88-4.93 0-2.85-1.98-4.89-4.88-4.89zm.13 7.54H2.26v-5.27h2.05c1.44 0 2.33 1.04 2.33 2.62 0 1.6-.9 2.65-2.33 2.65z" />
            </svg>
          </div>
        </div>
      </div>
    </footer>
  );
}
