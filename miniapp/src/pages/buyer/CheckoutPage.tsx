import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import { Icon } from "@/components/Icon";
import { PageHeader } from "@/components/PageHeader";
import { useToast } from "@/components/ui";
import { useAuth } from "@/store/auth";
import { useCart } from "@/store/cart";
import { getLocation, haptic } from "@/telegram/telegram";

const PAYMENTS = [
  { id: "cash", icon: "cash", key: "checkout.payCash" },
  { id: "click", icon: "card", label: "Click" },
  { id: "payme", icon: "card", label: "Payme" },
  { id: "uzum", icon: "card", label: "Uzum" },
];

export function CheckoutPage() {
  const { t } = useTranslation();
  const nav = useNavigate();
  const toast = useToast();
  const user = useAuth((s) => s.user);
  const cart = useCart();

  const [form, setForm] = useState({
    contact_name: user ? [user.first_name, user.last_name].filter(Boolean).join(" ") : "",
    phone: user?.phone || "",
    city: "",
    address: "",
    comment: "",
    payment_method: "cash",
  });
  const [submitting, setSubmitting] = useState(false);
  const [loc, setLoc] = useState<{ latitude: number; longitude: number } | null>(null);
  const [locating, setLocating] = useState(false);
  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const sendLocation = async () => {
    setLocating(true);
    try {
      const c = await getLocation();
      if (c) {
        setLoc(c);
        haptic("success");
        toast.show(t("checkout.locationOk"));
      } else {
        toast.show(t("checkout.locationFail"));
      }
    } finally {
      setLocating(false);
    }
  };

  const submit = async () => {
    if (!form.contact_name.trim() || !form.phone.trim() || (!form.address.trim() && !loc)) {
      toast.show(t("checkout.required"));
      return;
    }
    setSubmitting(true);
    try {
      const order = await api.checkout({ ...form, latitude: loc?.latitude ?? null, longitude: loc?.longitude ?? null });
      await cart.refresh();
      haptic("success");
      toast.show(t("checkout.success"));
      nav(`/orders/${order.id}`, { replace: true });
    } catch (e) {
      toast.show(e instanceof Error ? e.message : t("common.error"));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <PageHeader title={t("checkout.title")} />

      <div className="card card-pad mb">
        <div className="field">
          <label>{t("checkout.name")} *</label>
          <input className="input" value={form.contact_name} onChange={(e) => set("contact_name", e.target.value)} />
        </div>
        <div className="field">
          <label>{t("checkout.phone")} *</label>
          <input className="input" type="tel" value={form.phone} onChange={(e) => set("phone", e.target.value)} placeholder="+998" />
        </div>
        <div className="field">
          <label>{t("checkout.city")}</label>
          <input className="input" value={form.city} onChange={(e) => set("city", e.target.value)} />
        </div>
        <div className="field">
          <label>{t("checkout.address")}</label>
          <input className="input" value={form.address} onChange={(e) => set("address", e.target.value)} placeholder={t("checkout.addressHint")} />
        </div>
        <div className="field" style={{ marginBottom: 0 }}>
          <label>{t("checkout.comment")}</label>
          <textarea className="textarea" value={form.comment} onChange={(e) => set("comment", e.target.value)} />
        </div>
      </div>

      <div className="section-title">{t("checkout.delivery")}</div>
      <div className="card list-row" style={{ borderRadius: 14, cursor: "default" }}>
        <span className="icon-chip" style={{ width: 36, height: 36 }}><Icon name="truck" size={18} /></span>
        <span style={{ fontWeight: 600 }}>{t("checkout.deliveryOnly")}</span>
        <span className="badge badge-brand" style={{ marginLeft: "auto" }}><Icon name="check" size={12} strokeWidth={2.6} /></span>
      </div>

      <div className="section-title">{t("checkout.location")}</div>
      {loc ? (
        <div className="card list-row" style={{ borderRadius: 14, cursor: "default", borderColor: "var(--brand)", borderWidth: 1, borderStyle: "solid" }}>
          <span className="icon-chip" style={{ width: 36, height: 36, background: "var(--success-tint)", color: "var(--success)" }}><Icon name="pin" size={18} /></span>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontWeight: 600 }}>{t("checkout.locationOk")}</div>
            <a className="caption" href={`https://maps.google.com/?q=${loc.latitude},${loc.longitude}`} target="_blank" rel="noreferrer" style={{ color: "var(--brand)" }}>
              {loc.latitude.toFixed(5)}, {loc.longitude.toFixed(5)} — {t("checkout.openMap")}
            </a>
          </div>
          <button className="btn btn-sm btn-secondary" onClick={sendLocation}><Icon name="edit" size={14} /></button>
        </div>
      ) : (
        <button className="btn btn-secondary btn-block" disabled={locating} onClick={sendLocation}>
          {locating ? <span className="spin" /> : <Icon name="pin" size={18} />} {t("checkout.sendLocation")}
        </button>
      )}

      <div className="section-title">{t("checkout.payment")}</div>
      <div className="stack">
        {PAYMENTS.map((m) => {
          const active = form.payment_method === m.id;
          return (
            <div
              key={m.id}
              className="card list-row"
              style={{ borderRadius: 14, cursor: "pointer", borderColor: active ? "var(--brand)" : "var(--border)", borderWidth: 1, borderStyle: "solid" }}
              onClick={() => set("payment_method", m.id)}
            >
              <span className="icon-chip" style={{ width: 36, height: 36 }}><Icon name={m.icon} size={18} /></span>
              <span style={{ fontWeight: 600 }}>{m.label || t(m.key!)}</span>
              <span style={{ marginLeft: "auto", color: active ? "var(--brand)" : "var(--border-strong)" }}>
                <Icon name={active ? "check" : "chevron"} size={active ? 20 : 16} strokeWidth={active ? 2.6 : 1.75} />
              </span>
            </div>
          );
        })}
      </div>

      <div className="action-bar">
        <button className="btn btn-lg btn-block" disabled={submitting} onClick={submit}>
          {submitting ? <span className="spin" /> : <Icon name="check" size={18} />} {t("checkout.placeOrder")}
        </button>
      </div>
    </div>
  );
}
