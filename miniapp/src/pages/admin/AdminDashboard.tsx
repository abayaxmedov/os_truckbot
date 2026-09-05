import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import { Icon } from "@/components/Icon";
import { PageHeader } from "@/components/PageHeader";
import { SkeletonStats } from "@/components/Skeleton";
import { useApi } from "@/lib/useApi";
import { formatMoney } from "@/lib/format";

export function AdminDashboard() {
  const { t } = useTranslation();
  const nav = useNavigate();
  const { data, loading, error } = useApi(() => api.getAdminStats(), []);

  const menu = [
    { icon: "store", label: t("admin.sellers"), to: "/admin/sellers" },
    { icon: "wrench", label: t("admin.masters"), to: "/admin/masters" },
    { icon: "check", label: t("admin.moderation"), to: "/admin/moderation" },
    { icon: "grid", label: t("admin.categories"), to: "/admin/categories" },
    { icon: "percent", label: t("admin.commission"), to: "/admin/commission" },
    { icon: "card", label: t("admin.payouts"), to: "/admin/payouts" },
    { icon: "image", label: t("admin.banners"), to: "/admin/banners" },
    { icon: "link", label: t("admin.analogs"), to: "/admin/analogs" },
  ];

  return (
    <div>
      <PageHeader title={t("admin.title")} />
      {loading ? (
        <SkeletonStats count={6} />
      ) : error || !data ? (
        <div className="empty-state"><div className="es-ic"><Icon name="shield" size={30} /></div><div>{error}</div></div>
      ) : (
        <>
          <div className="card card-pad mb" style={{ background: "linear-gradient(120deg,var(--brand-700),var(--brand-500))", color: "#fff", border: 0 }}>
            <div className="caption" style={{ color: "rgba(255,255,255,.8)" }}>{t("admin.profit")}</div>
            <div className="tnum" style={{ fontSize: 30, fontWeight: 800, letterSpacing: "-0.02em" }}>{formatMoney(data.commission_total)} <span style={{ fontSize: 15, opacity: 0.8 }}>{t("common.sum")}</span></div>
            <div className="row mt" style={{ gap: 16, opacity: 0.9 }}>
              <span className="small">{t("admin.salesTotal")}: <b className="tnum">{formatMoney(data.sales_total)}</b></span>
            </div>
          </div>

          <div className="stat-grid">
            {[
              { ic: "box", v: data.orders_count, l: t("admin.ordersTotal") },
              { ic: "user", v: data.customers_count, l: t("admin.customers") },
              { ic: "store", v: data.sellers_count, l: t("admin.sellersCount") },
              { ic: "tag", v: data.products_count, l: t("admin.products") },
            ].map((s) => (
              <div className="stat" key={s.l}>
                <div className="stat-top"><span className="stat-ic"><Icon name={s.ic} size={17} /></span></div>
                <div className="val tnum">{s.v}</div>
                <div className="lbl">{s.l}</div>
              </div>
            ))}
          </div>
        </>
      )}

      <div className="list mt">
        {menu.map((m) => (
          <button className="list-row" key={m.to} onClick={() => nav(m.to)}>
            <span className="icon-chip" style={{ width: 34, height: 34 }}><Icon name={m.icon} size={17} /></span>
            <span>{m.label}</span>
            <Icon name="chevron" size={16} className="chevron" />
          </button>
        ))}
      </div>

      {data && data.popular_products.length > 0 && (
        <>
          <div className="section-head"><span className="sh-title">{t("admin.popular")}</span></div>
          <div className="list">
            {data.popular_products.map((p, i) => (
              <div className="list-row" key={p.id} style={{ cursor: "default" }}>
                <span className="tnum muted" style={{ width: 20, fontWeight: 700 }}>{i + 1}</span>
                <span style={{ flex: 1 }} className="small">{p.name_ru}</span>
                <span className="caption tnum">{p.sold} {t("admin.sold")}</span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
