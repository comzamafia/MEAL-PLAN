"use client";

import Link from "next/link";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { useCartStore } from "@/lib/store";

export function Header() {
  const [isOpen, setIsOpen] = useState(false);
  const totalItems = useCartStore((state) => state.getTotalItems());

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="container flex h-16 items-center justify-between px-4 md:px-6">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-600 text-white font-bold text-xl">
            W
          </div>
          <span className="hidden font-bold text-xl text-green-800 sm:block">
            Wela Meal Plan
          </span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-6">
          <Link
            href="/menu"
            className="text-sm font-medium text-gray-600 hover:text-green-600 transition-colors"
          >
            Menu
          </Link>
          <Link
            href="/#how-it-works"
            className="text-sm font-medium text-gray-600 hover:text-green-600 transition-colors"
          >
            How It Works
          </Link>
          <Link
            href="/#testimonials"
            className="text-sm font-medium text-gray-600 hover:text-green-600 transition-colors"
          >
            Reviews
          </Link>
          <Link
            href="/dashboard"
            className="text-sm font-medium text-gray-600 hover:text-green-600 transition-colors"
          >
            My Account
          </Link>
        </nav>

        {/* CTA & Cart */}
        <div className="flex items-center gap-4">
          <Button
            asChild
            className="hidden sm:flex bg-green-600 hover:bg-green-700"
          >
            <Link href="/checkout">Order Now</Link>
          </Button>

          {/* Cart indicator */}
          {totalItems > 0 && (
            <div className="relative">
              <Button variant="outline" size="icon" asChild>
                <Link href="/checkout">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <circle cx="8" cy="21" r="1" />
                    <circle cx="19" cy="21" r="1" />
                    <path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12" />
                  </svg>
                </Link>
              </Button>
              <span className="absolute -top-2 -right-2 flex h-5 w-5 items-center justify-center rounded-full bg-green-600 text-xs text-white">
                {totalItems}
              </span>
            </div>
          )}

          {/* Mobile Menu */}
          <Sheet open={isOpen} onOpenChange={setIsOpen}>
            <SheetTrigger asChild className="md:hidden">
              <Button variant="ghost" size="icon">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <line x1="4" x2="20" y1="12" y2="12" />
                  <line x1="4" x2="20" y1="6" y2="6" />
                  <line x1="4" x2="20" y1="18" y2="18" />
                </svg>
                <span className="sr-only">Toggle menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-[300px]">
              <nav className="flex flex-col gap-4 mt-8">
                <Link
                  href="/menu"
                  onClick={() => setIsOpen(false)}
                  className="text-lg font-medium"
                >
                  Menu
                </Link>
                <Link
                  href="/#how-it-works"
                  onClick={() => setIsOpen(false)}
                  className="text-lg font-medium"
                >
                  How It Works
                </Link>
                <Link
                  href="/#testimonials"
                  onClick={() => setIsOpen(false)}
                  className="text-lg font-medium"
                >
                  Reviews
                </Link>
                <Link
                  href="/dashboard"
                  onClick={() => setIsOpen(false)}
                  className="text-lg font-medium"
                >
                  My Account
                </Link>
                <Button
                  asChild
                  className="mt-4 bg-green-600 hover:bg-green-700"
                >
                  <Link href="/checkout" onClick={() => setIsOpen(false)}>
                    Order Now
                  </Link>
                </Button>
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}
