import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import type { Cart } from "@/api/types";
import { mediaUrl } from "@/api/client";
import { Icon } from "@/components/Icon";
import { Placeholder } from "@/components/Placeholder";
import { PageHeader } from "@/components/PageHeader";
import { QtyStepper } from "@/components/QtyStepper";
import { SkeletonCards } from "@/components/Skeleton";
import { Empty } from "@/components/ui";
import { useApi } from "@/lib/useApi";
import { formatMoney } from "@/lib/format";
import { useCart } from "@/store/cart";

export function CartPage() {
  const { t } = useTranslation();
  const nav = useNavigate();
  const cartStore = useCart();
  const { data, loading, setData } = useApi(() => api.getCart(), []);

  const apply = (cart: Cart) => {
    setData(cart);
    cartStore.setCount(cart.count);
  };

  const setQty = async (itemId: number, qty: number) => {
    if (qty < 1) apply(await api.removeCartItem(itemId));
    else apply(await api.updateCartItem(itemId, qty));
  };

  return (
    <div>
      <PageHeader title={t("cart.title")} subtitle={data && data.items.length > 0 ? `${data.count} ${t("orders.items")}` : undefined} />
      {loading ? (
        <SkeletonCards count={3} height={92} />
      ) : !data || data.items.length === 0 ? (
        <>
          <Empty icon="cart" text={t("cart.empty")} />
          <button className="btn btn-block" onClick={() => nav("/catalog")}>
            {t("cart.goShopping")}
          </button>
        </>
      ) : (
        <>
          <div className="stack">
            {data.items.map((it) => (
              <div className="card" key={it.id} style={{ padding: 10, display: "flex", gap: 12 }}>
                <div onClick={() => nav(`/product/${it.product_id}`)} style={{ flex: "0 0 68px", height: 68, borderRadius: 10, overflow: "hidden" }}>
                  {it.image ? (
                    <img src={mediaUrl(it.image)} style={{ width: 68, height: 68, objectFit: "cover" }} />
                  ) : (
                    <Placeholder size={26} />
                  )}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div className="small" style={{ fontWeight: 600, lineHeight: 1.3 }}>{it.name}</div>
                  <div className="caption">{it.seller_name}</div>
                  <div className="between mt-sm">
                    <div className="bold tnum">{formatMoney(it.line_total)} <span className="small muted">{t("common.sum")}</span></div>
                    <QtyStepper value={it.quantity} min={0} max={it.stock_qty} onChange={(v) => setQty(it.id, v)} />
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="card card-pad mt">
            <div className="between"><span className="muted">{t("cart.subtotal")}</span><span className="bold tnum">{formatMoney(data.subtotal)} {t("common.sum")}</span></div>
          </div>

          <div className="action-bar">
            <button className="btn btn-lg btn-block" onClick={() => nav("/checkout")}>
              <Icon name="check" size={18} /> {t("cart.checkout")} · <span className="tnum">{formatMoney(data.subtotal)}</span> {t("common.sum")}
            </button>
          </div>
        </>
      )}
    </div>
  );
}
