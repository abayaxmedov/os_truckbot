import { create } from "zustand";

import { authTelegram, getMe } from "@/api";
import type { User } from "@/api/types";
import { setToken } from "@/api/client";
import { getInitData } from "@/telegram/telegram";
import { setLanguage } from "@/i18n";

type Status = "idle" | "loading" | "ready" | "error";

interface AuthState {
  status: Status;
  token: string | null;
  user: User | null;
  error: string | null;
  login: () => Promise<void>;
  refresh: () => Promise<void>;
  setUser: (u: User) => void;
}

// Dev helper: when the app is opened outside Telegram (no initData), authenticate
// with a demo Telegram id so the app is fully usable in a normal browser.
// Switch roles by URL: ?dev_tg=100000001 (admin) / 100000002 (seller) / 100000004 (buyer)
function devTelegramId(): number | undefined {
  if (getInitData()) return undefined;
  const param = new URLSearchParams(window.location.search).get("dev_tg");
  if (param && /^\d+$/.test(param)) return Number(param);
  const env = import.meta.env.VITE_DEV_TG as string | undefined;
  if (env && /^\d+$/.test(env)) return Number(env);
  return 100000004; // demo buyer
}

export const useAuth = create<AuthState>((set, get) => ({
  status: "idle",
  token: null,
  user: null,
  error: null,

  login: async () => {
    set({ status: "loading", error: null });
    try {
      const res = await authTelegram(getInitData(), devTelegramId());
      setToken(res.token);
      setLanguage(res.user.language);
      set({ status: "ready", token: res.token, user: res.user });
    } catch (e) {
      set({ status: "error", error: e instanceof Error ? e.message : "auth_failed" });
    }
  },

  refresh: async () => {
    if (!get().token) return;
    const user = await getMe();
    set({ user });
  },

  setUser: (u: User) => set({ user: u }),
}));
