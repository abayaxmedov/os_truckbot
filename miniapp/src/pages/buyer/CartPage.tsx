import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { mediaUrl } from "@/api/client";
import { Icon } from "@/components/Icon";
import { Placeholder } from "@/components/Placeholder";
import { PageHeader } from "@/components/PageHeader";
import { QtyStepper } from "@/components/QtyStepper";
import { SkeletonCards } from "@/components/Skeleton";
import { Empty } from "@/components/ui";
import { formatMoney } from "@/lib/format";
import { hasMainButton, useMainButton } from "@/lib/useMainButton";
import { useCart } from "@/store/cart";

export function CartPage() {
  const { t } = useTranslation();
  const nav = useNavigate();
  const items = useCart((s) => s.items);
  const subtotal = useCart((s) => s.subtotal);
  const count = useCart((s) => s.count);
  const refresh = useCart((s) => s.refresh);
  const setQty = useCart((s) => s.setQty);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    refresh().finally(() => setLoading(false));
  }, [refresh]);

  const goCheckout = useCallback(() => nav("/checkout"), [nav]);
  useMainButton(`${t("cart.checkout")} · ${formatMoney(subtotal)}`, goCheckout, {
    visible: items.length > 0,
  });

  return (
    <div>
      <PageHeader title={t("cart.title")} subtitle={items.length > 0 ? `${count} ${t("orders.items")}` : undefined} />
      {loading ? (
        <SkeletonCards count={3} height={92} />
      ) : items.length === 0 ? (
        <div className="empty-wrap">
          <Empty icon="cart" text={t("cart.empty")} hint={t("cart.emptyHint")} />
          <button className="btn btn-lg" style={{ minWidth: 220 }} onClick={() => nav("/catalog")}>
            <Icon name="grid" size={18} /> {t("cart.goShopping")}
          </button>
        </div>
      ) : (
        <>
          <div className="stack">
            {items.map((it) => (
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
            <div className="between"><span className="muted">{t("cart.subtotal")}</span><span className="bold tnum">{formatMoney(subtotal)} {t("common.sum")}</span></div>
          </div>

          {!hasMainButton() && (
            <div className="action-bar">
              <button className="btn btn-lg btn-block" onClick={goCheckout}>
                <Icon name="check" size={18} /> {t("cart.checkout")} · <span className="tnum">{formatMoney(subtotal)}</span> {t("common.sum")}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
