import { create } from "zustand";

import { getCart } from "@/api";

interface CartState {
  count: number;
  setCount: (n: number) => void;
  refresh: () => Promise<void>;
}

export const useCart = create<CartState>((set) => ({
  count: 0,
  setCount: (n: number) => set({ count: n }),
  refresh: async () => {
    try {
      const cart = await getCart();
      set({ count: cart.count });
    } catch {
      /* ignore */
    }
  },
}));
