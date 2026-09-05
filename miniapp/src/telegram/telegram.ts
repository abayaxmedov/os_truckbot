// Thin, dependency-free wrapper around the official Telegram Mini App SDK
// (window.Telegram.WebApp, loaded via telegram-web-app.js in index.html).

type ThemeParams = Record<string, string>;

interface TgWebApp {
  initData: string;
  initDataUnsafe: { user?: { id: number; first_name?: string; language_code?: string } };
  colorScheme: "light" | "dark";
  themeParams: ThemeParams;
  version: string;
  isExpanded: boolean;
  ready: () => void;
  expand: () => void;
  close: () => void;
  setHeaderColor?: (color: string) => void;
  setBackgroundColor?: (color: string) => void;
  openTelegramLink?: (url: string) => void;
  openLink?: (url: string, options?: Record<string, unknown>) => void;
  onEvent: (type: string, cb: () => void) => void;
  offEvent: (type: string, cb: () => void) => void;
  BackButton: { show: () => void; hide: () => void; onClick: (cb: () => void) => void; offClick: (cb: () => void) => void };
  MainButton: {
    setText: (t: string) => void;
    show: () => void;
    hide: () => void;
    enable: () => void;
    disable: () => void;
    showProgress: (leaveActive?: boolean) => void;
    hideProgress: () => void;
    onClick: (cb: () => void) => void;
    offClick: (cb: () => void) => void;
    setParams: (p: Record<string, unknown>) => void;
  };
  HapticFeedback?: {
    impactOccurred: (style: string) => void;
    notificationOccurred: (type: string) => void;
    selectionChanged: () => void;
  };
}

declare global {
  interface Window {
    Telegram?: { WebApp?: TgWebApp };
  }
}

export function getWebApp(): TgWebApp | null {
  return window.Telegram?.WebApp ?? null;
}

function applyTheme(scheme: "light" | "dark") {
  document.documentElement.dataset.theme = scheme;
  const wa = getWebApp();
  const bg = scheme === "dark" ? "#0a0f1a" : "#f5f7fa";
  try {
    wa?.setBackgroundColor?.(bg);
    wa?.setHeaderColor?.(bg);
  } catch {
    /* ignore */
  }
}

export function initTelegram(): void {
  const wa = getWebApp();
  // Follow Telegram's (or the OS') light/dark preference with our own token palette.
  const scheme = wa?.colorScheme ?? (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  applyTheme(scheme);
  if (!wa) return;
  try {
    wa.ready();
    wa.expand();
    wa.onEvent("themeChanged", () => applyTheme(wa.colorScheme));
  } catch {
    /* ignore */
  }
}

export function getInitData(): string {
  return getWebApp()?.initData ?? "";
}

export function getTgUser() {
  return getWebApp()?.initDataUnsafe?.user ?? null;
}

export function getColorScheme(): "light" | "dark" {
  return getWebApp()?.colorScheme ?? "light";
}

export function getThemeParams(): ThemeParams {
  return getWebApp()?.themeParams ?? {};
}

export function haptic(type: "light" | "medium" | "heavy" | "success" | "error" | "warning" = "light") {
  const hf = getWebApp()?.HapticFeedback;
  if (!hf) return;
  try {
    if (type === "success" || type === "error" || type === "warning") hf.notificationOccurred(type);
    else hf.impactOccurred(type);
  } catch {
    /* ignore */
  }
}

// ---- BackButton helpers ----
export function showBackButton(onClick: () => void): () => void {
  const bb = getWebApp()?.BackButton;
  if (!bb) return () => {};
  bb.onClick(onClick);
  bb.show();
  return () => {
    bb.offClick(onClick);
    bb.hide();
  };
}

// ---- MainButton helpers ----
export function setMainButton(
  text: string,
  onClick: () => void,
  opts?: { visible?: boolean; enabled?: boolean; progress?: boolean },
): () => void {
  const mb = getWebApp()?.MainButton;
  if (!mb) return () => {};
  mb.setText(text);
  mb.onClick(onClick);
  if (opts?.progress) mb.showProgress();
  else mb.hideProgress();
  if (opts?.enabled === false) mb.disable();
  else mb.enable();
  if (opts?.visible === false) mb.hide();
  else mb.show();
  return () => {
    mb.offClick(onClick);
    mb.hide();
    mb.hideProgress();
  };
}

// ---- Location ----
export interface Coords {
  latitude: number;
  longitude: number;
}

/** Get the user's location via Telegram LocationManager (Bot API 8.0+) or the
 *  browser geolocation API. Resolves null if unavailable or denied. */
export function getLocation(): Promise<Coords | null> {
  return new Promise((resolve) => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const lm = (getWebApp() as any)?.LocationManager;

    const browser = () => {
      if (!navigator.geolocation) return resolve(null);
      navigator.geolocation.getCurrentPosition(
        (pos) => resolve({ latitude: pos.coords.latitude, longitude: pos.coords.longitude }),
        () => resolve(null),
        { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 },
      );
    };

    if (lm && typeof lm.getLocation === "function") {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const read = () => lm.getLocation((loc: any) =>
        resolve(loc && typeof loc.latitude === "number"
          ? { latitude: loc.latitude, longitude: loc.longitude }
          : null),
      );
      try {
        if (lm.isInited) read();
        else lm.init(read);
      } catch {
        browser();
      }
      return;
    }
    browser();
  });
}

/** Open a Telegram chat by @handle. Uses the native Mini App API when available,
 *  falling back to a normal t.me link. */
export function openTelegramHandle(handle: string): void {
  const clean = handle.trim().replace(/^@/, "");
  if (!clean) return;
  const url = `https://t.me/${clean}`;
  const wa = getWebApp();
  if (wa?.openTelegramLink) wa.openTelegramLink(url);
  else window.open(url, "_blank");
}
