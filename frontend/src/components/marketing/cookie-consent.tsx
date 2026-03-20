"use client";

import { useState, useEffect, useRef, useCallback, useSyncExternalStore } from "react";
import { Button } from "@/components/ui/button";

const emptySubscribe = () => () => {};
const returnTrue = () => true;
const returnFalse = () => false;

const CONSENT_KEY = "wela-cookie-consent";

type ConsentState = {
  necessary: boolean;
  analytics: boolean;
  marketing: boolean;
  timestamp: string;
};

const defaultConsent: ConsentState = {
  necessary: true,
  analytics: false,
  marketing: false,
  timestamp: "",
};

function loadGoogleAnalytics() {
  const gaId = process.env.NEXT_PUBLIC_GA4_ID;
  if (!gaId) return;

  const script = document.createElement("script");
  script.src = `https://www.googletagmanager.com/gtag/js?id=${gaId}`;
  script.async = true;
  document.head.appendChild(script);

  window.dataLayer = window.dataLayer || [];
  function gtag(...args: unknown[]) {
    window.dataLayer.push(args);
  }
  gtag("js", new Date());
  gtag("config", gaId);
}

function loadMetaPixel() {
  const pixelId = process.env.NEXT_PUBLIC_META_PIXEL_ID;
  if (!pixelId) return;
  console.log("[Meta Pixel] Would load pixel:", pixelId);
}

function readStoredConsent(): ConsentState | null {
  try {
    const stored = localStorage.getItem(CONSENT_KEY);
    if (!stored) return null;
    return JSON.parse(stored) as ConsentState;
  } catch {
    return null;
  }
}

function CookieConsentInner() {
  const [showBanner, setShowBanner] = useState(() => {
    return readStoredConsent() === null;
  });
  const [showDetails, setShowDetails] = useState(false);
  const [consent, setConsent] = useState<ConsentState>(() => {
    return readStoredConsent() ?? defaultConsent;
  });
  const scriptsLoaded = useRef(false);

  useEffect(() => {
    if (scriptsLoaded.current) return;
    scriptsLoaded.current = true;

    if (consent.analytics) loadGoogleAnalytics();
    if (consent.marketing) loadMetaPixel();
  }, [consent.analytics, consent.marketing]);

  const saveConsent = useCallback((newConsent: ConsentState) => {
    localStorage.setItem(CONSENT_KEY, JSON.stringify(newConsent));
    setConsent(newConsent);
    setShowBanner(false);

    if (newConsent.analytics) loadGoogleAnalytics();
    if (newConsent.marketing) loadMetaPixel();
  }, []);

  const acceptAll = useCallback(() => {
    saveConsent({
      necessary: true,
      analytics: true,
      marketing: true,
      timestamp: new Date().toISOString(),
    });
  }, [saveConsent]);

  const acceptNecessary = useCallback(() => {
    saveConsent({
      necessary: true,
      analytics: false,
      marketing: false,
      timestamp: new Date().toISOString(),
    });
  }, [saveConsent]);

  const savePreferences = useCallback(() => {
    saveConsent({
      ...consent,
      timestamp: new Date().toISOString(),
    });
  }, [consent, saveConsent]);

  if (!showBanner) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 p-4 bg-white border-t shadow-lg">
      <div className="container max-w-4xl mx-auto">
        {!showDetails ? (
          <div className="flex flex-col md:flex-row items-start md:items-center gap-4">
            <div className="flex-1">
              <p className="text-sm text-gray-700">
                We use cookies to enhance your experience. By continuing to visit this site,
                you agree to our use of cookies.{" "}
                <button
                  onClick={() => setShowDetails(true)}
                  className="text-green-600 hover:underline"
                >
                  Customize preferences
                </button>
              </p>
            </div>
            <div className="flex gap-2 shrink-0">
              <Button
                variant="outline"
                size="sm"
                onClick={acceptNecessary}
              >
                Necessary Only
              </Button>
              <Button
                size="sm"
                className="bg-green-600 hover:bg-green-700"
                onClick={acceptAll}
              >
                Accept All
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <h3 className="font-semibold">Cookie Preferences</h3>
            <p className="text-sm text-gray-600">
              This website uses cookies to improve your experience and analyze site traffic.
              You can customize your preferences below. We respect your privacy in accordance
              with CASL (Canada&apos;s Anti-Spam Legislation) and PIPEDA.
            </p>

            <div className="space-y-3">
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={consent.necessary}
                  disabled
                  className="h-4 w-4"
                />
                <div>
                  <span className="font-medium text-sm">Necessary Cookies</span>
                  <span className="text-xs text-gray-500 ml-2">(Required)</span>
                  <p className="text-xs text-gray-500">
                    Essential for the website to function properly. Cannot be disabled.
                  </p>
                </div>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={consent.analytics}
                  onChange={(e) =>
                    setConsent({ ...consent, analytics: e.target.checked })
                  }
                  className="h-4 w-4"
                />
                <div>
                  <span className="font-medium text-sm">Analytics Cookies</span>
                  <p className="text-xs text-gray-500">
                    Help us understand how visitors interact with our website (Google Analytics).
                  </p>
                </div>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={consent.marketing}
                  onChange={(e) =>
                    setConsent({ ...consent, marketing: e.target.checked })
                  }
                  className="h-4 w-4"
                />
                <div>
                  <span className="font-medium text-sm">Marketing Cookies</span>
                  <p className="text-xs text-gray-500">
                    Used to show you relevant ads on other platforms (Meta Pixel).
                  </p>
                </div>
              </label>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowDetails(false)}
              >
                Back
              </Button>
              <Button
                size="sm"
                className="bg-green-600 hover:bg-green-700"
                onClick={savePreferences}
              >
                Save Preferences
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export function CookieConsent() {
  const isMounted = useSyncExternalStore(emptySubscribe, returnTrue, returnFalse);

  if (!isMounted) return null;

  return <CookieConsentInner />;
}

declare global {
  interface Window {
    dataLayer: unknown[];
  }
}
