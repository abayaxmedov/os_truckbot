import { create } from "zustand";

import * as api from "@/api";
import type { Cart, CartItem } from "@/api/types";
import { haptic } from "@/telegram/telegram";

interface CartState {
  items: CartItem[];
  count: number;
  subtotal: number;
  setCart: (cart: Cart) => void;
  setCount: (n: number) => void;
  refresh: () => Promise<void>;
  qtyOf: (productId: number) => number;
  /** Add (or increment by delta) a product; returns the new quantity. */
  add: (productId: number, delta?: number) => Promise<void>;
  /** Set the quantity for a product by its cart-item id (0 removes it). */
  setQty: (itemId: number, quantity: number) => Promise<void>;
  /** Set quantity for a product id (finds the cart item; 0 removes). */
  setQtyByProduct: (productId: number, quantity: number) => Promise<void>;
}

export const useCart = create<CartState>((set, get) => ({
  items: [],
  count: 0,
  subtotal: 0,
  setCart: (cart) => set({ items: cart.items, count: cart.count, subtotal: cart.subtotal }),
  setCount: (n) => set({ count: n }),
  refresh: async () => {
    try {
      get().setCart(await api.getCart());
    } catch {
      /* ignore */
    }
  },
  qtyOf: (productId) => get().items.find((i) => i.product_id === productId)?.quantity ?? 0,
  add: async (productId, delta = 1) => {
    const cart = await api.addToCart(productId, delta);
    get().setCart(cart);
    haptic("light");
  },
  setQty: async (itemId, quantity) => {
    const cart = quantity < 1 ? await api.removeCartItem(itemId) : await api.updateCartItem(itemId, quantity);
    get().setCart(cart);
  },
  setQtyByProduct: async (productId, quantity) => {
    const item = get().items.find((i) => i.product_id === productId);
    if (!item) {
      if (quantity > 0) await get().add(productId, quantity);
      return;
    }
    await get().setQty(item.id, quantity);
  },
}));
