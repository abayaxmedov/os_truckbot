import { useTranslation } from "react-i18next";

import * as api from "@/api";
import { Icon } from "@/components/Icon";
import { PageHeader } from "@/components/PageHeader";
import { SelectSheet } from "@/components/SelectSheet";
import { SkeletonCards } from "@/components/Skeleton";
import { Empty, StatusBadge, useToast } from "@/components/ui";
import { useApi } from "@/lib/useApi";
import { formatMoney } from "@/lib/format";

const STATUSES = ["new", "confirmed", "processing", "shipped", "delivered", "completed", "cancelled"];

export function SellerOrdersPage() {
  const { t } = useTranslation();
  const toast = useToast();
  const { data, loading, reload } = useApi(() => api.getSellerOrders(), []);

  const change = async (id: number, status: string) => {
    await api.updateSellerOrderStatus(id, status);
    toast.show(t("profile.saved"));
    reload();
  };

  return (
    <div>
      <PageHeader title={t("seller.orders")} />
      {loading ? (
        <SkeletonCards count={3} height={140} />
      ) : (data || []).length === 0 ? (
        <Empty icon="cart" text={t("orders.empty")} />
      ) : (
        <div className="stack">
          {(data || []).map((o) => (
            <div className="card card-pad" key={o.id}>
              <div className="between mb">
                <span className="bold">{t("orders.order")} #{o.order_id}</span>
                <StatusBadge status={o.status} />
              </div>
              <div className="caption row" style={{ gap: 6 }}><Icon name="user" size={13} /> {o.buyer_name} · {o.phone}</div>
              {(o.city || o.address) && <div className="caption row mt-sm" style={{ gap: 6 }}><Icon name="pin" size={13} /> {o.city} {o.address}</div>}
              {o.latitude != null && o.longitude != null && (
                <a className="row mt-sm" style={{ gap: 6, color: "var(--brand)", fontWeight: 600, fontSize: 13 }}
                  href={`https://maps.google.com/?q=${o.latitude},${o.longitude}`} target="_blank" rel="noreferrer">
                  <Icon name="pin" size={14} /> {t("checkout.openMap")}
                </a>
              )}
              <div className="mt-sm" style={{ borderTop: "1px solid var(--border)", paddingTop: 8 }}>
                {o.items.map((it) => (
                  <div className="between" key={it.id} style={{ padding: "3px 0" }}>
                    <span className="small">{it.product_name} <span className="muted">× {it.quantity}</span></span>
                    <span className="small tnum">{formatMoney(it.line_total)}</span>
                  </div>
                ))}
              </div>
              <div className="between mt">
                <span className="caption">{t("seller.payout")}</span>
                <span className="bold tnum">{formatMoney(o.seller_payout)} {t("common.sum")}</span>
              </div>
              <div className="field mt" style={{ marginBottom: 0 }}>
                <label>{t("seller.changeStatus")}</label>
                <SelectSheet
                  icon="box"
                  title={t("seller.changeStatus")}
                  value={o.status}
                  onChange={(v) => change(o.id, String(v))}
                  options={STATUSES.map((s) => ({ value: s, label: t(`status.${s}`) }))}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
