import { useTranslation } from "react-i18next";

import { Icon } from "@/components/Icon";
import { useCart } from "@/store/cart";

// Add-to-cart control: shows a "+" button; once in the cart it becomes a −/qty/+
// stepper so the buyer picks how many. Used on product cards and the product page.
export function CartControl({
  productId,
  inStock = true,
  stockQty = 9999,
  variant = "card",
}: {
  productId: number;
  inStock?: boolean;
  stockQty?: number;
  variant?: "card" | "page";
}) {
  const { t } = useTranslation();
  const items = useCart((s) => s.items);
  const qty = items.find((i) => i.product_id === productId)?.quantity ?? 0;
  const add = useCart((s) => s.add);
  const setQtyByProduct = useCart((s) => s.setQtyByProduct);
  const stop = (e: React.MouseEvent) => e.stopPropagation();

  if (qty === 0) {
    if (variant === "page") {
      return (
        <button className="btn btn-block" disabled={!inStock} onClick={(e) => { stop(e); add(productId); }}>
          <Icon name="cart" size={18} /> {t("product.addToCart")}
        </button>
      );
    }
    return (
      <button className="cart-add" disabled={!inStock} onClick={(e) => { stop(e); add(productId); }} aria-label={t("product.addToCart")}>
        <Icon name="cart" size={17} />
      </button>
    );
  }

  const stepper = (big: boolean) => (
    <div className={big ? "qty-mini qty-lg" : "qty-mini"} onClick={stop}>
      <button onClick={() => setQtyByProduct(productId, qty - 1)}>
        <Icon name={qty === 1 ? "trash" : "minus"} size={big ? 18 : 15} strokeWidth={2.2} />
      </button>
      <span className="tnum">{qty}</span>
      <button disabled={qty >= stockQty} onClick={() => setQtyByProduct(productId, qty + 1)}>
        <Icon name="plus" size={big ? 18 : 15} strokeWidth={2.2} />
      </button>
    </div>
  );

  return variant === "page" ? <div style={{ flex: 1 }}>{stepper(true)}</div> : stepper(false);
}
