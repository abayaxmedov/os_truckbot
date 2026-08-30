import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import type { SellerStats } from "@/api/types";
import { Icon } from "@/components/Icon";
import { PageHeader } from "@/components/PageHeader";
import { SkeletonStats } from "@/components/Skeleton";
import { Stars, useToast } from "@/components/ui";
import { useApi } from "@/lib/useApi";
import { formatMoney } from "@/lib/format";
import { useAuth } from "@/store/auth";

function RegisterForm() {
  const { t } = useTranslation();
  const toast = useToast();
  const refresh = useAuth((s) => s.refresh);
  const [shop, setShop] = useState("");
  const [desc, setDesc] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    if (!shop.trim()) return;
    setBusy(true);
    try {
      await api.sellerRegister(shop.trim(), desc.trim());
      await refresh();
      toast.show(t("profile.saved"));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <div className="center" style={{ padding: "12px 0 20px" }}>
        <span className="icon-chip" style={{ width: 64, height: 64 }}><Icon name="store" size={30} /></span>
        <div className="page-title mt" style={{ fontSize: 21 }}>{t("seller.register")}</div>
      </div>
      <div className="card card-pad">
        <div className="field">
          <label>{t("seller.shopName")} *</label>
          <input className="input" value={shop} onChange={(e) => setShop(e.target.value)} />
        </div>
        <div className="field" style={{ marginBottom: 14 }}>
          <label>{t("seller.description")}</label>
          <textarea className="textarea" value={desc} onChange={(e) => setDesc(e.target.value)} />
        </div>
        <button className="btn btn-block" disabled={busy} onClick={submit}>
          {busy ? <span className="spin" /> : null} {t("seller.registerBtn")}
        </button>
      </div>
    </div>
  );
}

export function SellerDashboard() {
  const user = useAuth((s) => s.user);
  if (!user?.is_seller) return <RegisterForm />;
  return <SellerHome />;
}

function SellerHome() {
  const { t } = useTranslation();
  const nav = useNavigate();
  const { data, loading } = useApi<SellerStats>(() => api.getSellerStats(), []);

  const menu = [
    { icon: "box", label: t("seller.products"), to: "/seller/products", n: data?.products_count },
    { icon: "cart", label: t("seller.orders"), to: "/seller/orders", n: data?.orders_count },
    { icon: "plus", label: t("seller.addProduct"), to: "/seller/products/new" },
    { icon: "upload", label: t("seller.bulkImport"), to: "/seller/import" },
  ];

  return (
    <div>
      <PageHeader title={t("seller.title")} />
      {loading || !data ? (
        <SkeletonStats count={4} />
      ) : (
        <div className="stat-grid">
          <div className="stat"><div className="stat-top"><span className="stat-ic"><Icon name="chart" size={17} /></span></div><div className="val tnum">{formatMoney(data.sales_total)}</div><div className="lbl">{t("seller.sales")}</div></div>
          <div className="stat"><div className="stat-top"><span className="stat-ic"><Icon name="cash" size={17} /></span></div><div className="val tnum">{formatMoney(data.payout_total)}</div><div className="lbl">{t("seller.payout")}</div></div>
          <div className="stat"><div className="stat-top"><span className="stat-ic"><Icon name="percent" size={17} /></span></div><div className="val tnum">{formatMoney(data.commission_total)}</div><div className="lbl">{t("seller.commission")}</div></div>
          <div className="stat"><div className="stat-top"><span className="stat-ic"><Icon name="star" size={17} /></span></div><div className="val row" style={{ gap: 6 }}><Stars value={data.rating} size={15} /> {data.rating.toFixed(1)}</div><div className="lbl">{t("seller.rating")} · {data.completion_rate.toFixed(0)}%</div></div>
        </div>
      )}

      <div className="list mt">
        {menu.map((m) => (
          <button className="list-row" key={m.to} onClick={() => nav(m.to)}>
            <span className="icon-chip" style={{ width: 34, height: 34 }}><Icon name={m.icon} size={17} /></span>
            <span>{m.label}</span>
            <span className="chevron">{m.n != null ? m.n : ""} <Icon name="chevron" size={16} /></span>
          </button>
        ))}
      </div>
    </div>
  );
}
