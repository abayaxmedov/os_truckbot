import { useState } from "react";
import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import type { SellerOrder } from "@/api/types";
import { Icon } from "@/components/Icon";
import { PageHeader } from "@/components/PageHeader";
import { Sheet } from "@/components/Sheet";
import { Loader, StatusBadge, useToast } from "@/components/ui";
import { useApi } from "@/lib/useApi";
import { formatMoney } from "@/lib/format";
import { haptic } from "@/telegram/telegram";

export function OrderDetailPage() {
  const { id } = useParams();
  const oid = Number(id);
  const { t } = useTranslation();
  const toast = useToast();
  const { data: order, loading, reload } = useApi(() => api.getOrder(oid), [oid]);

  const [reviewFor, setReviewFor] = useState<SellerOrder | null>(null);
  const [stars, setStars] = useState(5);
  const [comment, setComment] = useState("");

  if (loading || !order) return <Loader />;

  const submitReview = async () => {
    if (!reviewFor) return;
    await api.createReview(reviewFor.id, stars, comment);
    setReviewFor(null);
    setComment("");
    setStars(5);
    haptic("success");
    toast.show(t("orders.reviewSent"));
    reload();
  };

  const pay = async () => {
    const res = await api.payOrder(order.id, order.payment_method);
    if (res.payment_url) window.open(res.payment_url, "_blank");
  };

  const infoRow = (icon: string, label: string, value: React.ReactNode) => (
    <div className="between" style={{ padding: "8px 0" }}>
      <span className="row muted small" style={{ gap: 8 }}><Icon name={icon} size={15} /> {label}</span>
      <span className="small" style={{ textAlign: "right", fontWeight: 600 }}>{value}</span>
    </div>
  );

  return (
    <div>
      <PageHeader title={`${t("orders.order")} #${order.id}`} action={<StatusBadge status={order.status_summary} />} />

      <div className="card card-pad mb">
        {infoRow("user", t("checkout.name"), order.contact_name)}
        {infoRow("phone", t("checkout.phone"), order.phone)}
        {(order.city || order.address) && infoRow("pin", t("checkout.address"), `${order.city} ${order.address}`)}
        {infoRow("card", t("orders.payment"), <StatusBadge status={order.payment_status} />)}
      </div>

      {order.seller_orders.map((so) => (
        <div className="card card-pad mb" key={so.id}>
          <div className="between mb">
            <span className="row bold" style={{ gap: 8 }}><Icon name="store" size={17} /> {so.seller_name}</span>
            <StatusBadge status={so.status} />
          </div>
          {so.items.map((it) => (
            <div className="between" key={it.id} style={{ padding: "7px 0", borderBottom: "1px solid var(--border)" }}>
              <span className="small">{it.product_name} <span className="muted">× {it.quantity}</span></span>
              <span className="small bold tnum">{formatMoney(it.line_total)}</span>
            </div>
          ))}
          <div className="between mt"><span className="muted small">{t("cart.subtotal")}</span><span className="bold tnum">{formatMoney(so.subtotal)} {t("common.sum")}</span></div>
          {so.can_review && (
            <button className="btn btn-outline btn-block mt" onClick={() => setReviewFor(so)}>
              <Icon name="star" size={16} /> {t("orders.leaveReview")}
            </button>
          )}
          {so.reviewed && <div className="center caption mt">{t("orders.reviewed")}</div>}
        </div>
      ))}

      <div className="card card-pad">
        <div className="between"><span className="muted">{t("cart.subtotal")}</span><span className="tnum">{formatMoney(order.subtotal)} {t("common.sum")}</span></div>
        <div className="between mt-sm"><span className="muted">{t("cart.delivery")}</span><span className="tnum">{formatMoney(order.delivery_cost)} {t("common.sum")}</span></div>
        <div className="between mt" style={{ paddingTop: 10, borderTop: "1px solid var(--border)" }}>
          <span className="bold">{t("cart.total")}</span>
          <span className="bold tnum" style={{ fontSize: 19 }}>{formatMoney(order.total)} {t("common.sum")}</span>
        </div>
      </div>

      {order.payment_status === "pending" && order.payment_method !== "cash" && (
        <div className="action-bar">
          <button className="btn btn-block" onClick={pay}><Icon name="card" size={18} /> {t("orders.pay")} ({order.payment_method})</button>
        </div>
      )}

      <Sheet open={!!reviewFor} onClose={() => setReviewFor(null)} title={`${t("orders.leaveReview")} · ${reviewFor?.seller_name ?? ""}`}>
        <div className="center" style={{ display: "flex", justifyContent: "center", gap: 8, margin: "8px 0 4px" }}>
          {[1, 2, 3, 4, 5].map((n) => (
            <span key={n} onClick={() => setStars(n)} style={{ cursor: "pointer", color: n <= stars ? "var(--star)" : "var(--border-strong)" }}>
              <Icon name="star" size={38} fill={n <= stars} strokeWidth={1.25} />
            </span>
          ))}
        </div>
        <textarea className="textarea mt" value={comment} onChange={(e) => setComment(e.target.value)} placeholder={t("product.description")} />
        <button className="btn btn-block mt" onClick={submitReview}>{t("common.send")}</button>
      </Sheet>
    </div>
  );
}
