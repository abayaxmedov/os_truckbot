import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import { mediaUrl } from "@/api/client";
import { Icon } from "@/components/Icon";
import { Loader } from "@/components/ui";
import { useApi } from "@/lib/useApi";
import { formatMoney } from "@/lib/format";
import { labelsFor, SPECIALIZATIONS, TRUCKS } from "@/lib/masterOptions";
import { haptic } from "@/telegram/telegram";

export function MasterDetailPage() {
  const { id } = useParams();
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const { data: m, loading } = useApi(() => api.getMasterPublic(Number(id)), [id]);

  if (loading || !m) return <Loader />;
  const trucks = labelsFor(TRUCKS, m.trucks, lang);
  const specs = labelsFor(SPECIALIZATIONS, m.specializations, lang);

  const call = () => {
    haptic("success");
    if (m.phone) window.location.href = `tel:${m.phone}`;
  };

  const row = (icon: string, label: string, value?: string | null) =>
    value ? (
      <div className="between" style={{ padding: "11px 0", borderBottom: "1px solid var(--border)" }}>
        <span className="row muted small" style={{ gap: 8 }}><Icon name={icon} size={16} /> {label}</span>
        <span className="small" style={{ textAlign: "right", maxWidth: "58%", fontWeight: 600 }}>{value}</span>
      </div>
    ) : null;

  return (
    <div>
      {/* Header */}
      <div className="center" style={{ padding: "8px 0 14px" }}>
        {m.photo ? (
          <img src={mediaUrl(m.photo)} style={{ width: 96, height: 96, borderRadius: "50%", objectFit: "cover" }} alt={m.name} />
        ) : (
          <span className="icon-chip" style={{ width: 96, height: 96 }}><Icon name="user" size={40} /></span>
        )}
        <div className="row center" style={{ gap: 8, marginTop: 12, justifyContent: "center", flexWrap: "wrap" }}>
          <span className="page-title" style={{ fontSize: 22 }}>{m.name || "—"}</span>
          {m.is_verified && (
            <span className="badge badge-green" style={{ gap: 4 }}><Icon name="check" size={13} strokeWidth={3} /> {t("master.verified")}</span>
          )}
        </div>
        {(m.is_24_7 || m.work_hours) && (
          <div className="muted small mt-sm">{m.is_24_7 ? `🚨 ${t("master.is247")}` : m.work_hours}</div>
        )}
      </div>

      {trucks.length > 0 && (
        <>
          <div className="section-title">{t("master.trucks")}</div>
          <div className="master-tags mb">
            {trucks.map((l) => <span key={l} className="mtag mtag-truck">🚛 {l}</span>)}
          </div>
        </>
      )}
      {specs.length > 0 && (
        <>
          <div className="section-title">{t("master.specializations")}</div>
          <div className="master-tags mb">
            {specs.map((l) => <span key={l} className="mtag">🛠 {l}</span>)}
          </div>
        </>
      )}

      {(m.price_call != null || m.price_diagnostics != null || m.price_repair_note) && (
        <>
          <div className="section-title">{t("master.prices")}</div>
          <div className="card card-pad mb">
            {m.price_call != null && <div className="between" style={{ padding: "4px 0" }}><span className="muted small">{t("master.priceCall")}</span><b className="tnum">{formatMoney(m.price_call)} {t("common.sum")}</b></div>}
            {m.price_diagnostics != null && <div className="between" style={{ padding: "4px 0" }}><span className="muted small">{t("master.priceDiagnostics")}</span><b className="tnum">{formatMoney(m.price_diagnostics)} {t("common.sum")}</b></div>}
            {m.price_repair_note && <div className="between" style={{ padding: "4px 0" }}><span className="muted small">{t("master.priceRepair")}</span><b>{m.price_repair_note}</b></div>}
          </div>
        </>
      )}

      {m.bio && (
        <>
          <div className="section-title">{t("master.bio")}</div>
          <div className="card card-pad mb" style={{ lineHeight: 1.55 }}>{m.bio}</div>
        </>
      )}

      <div className="card card-pad" style={{ paddingTop: 4, paddingBottom: 4 }}>
        {row("pin", t("master.regions"), m.regions)}
        {row("shield", t("master.experience"), m.experience_years ? `${m.experience_years} ${t("master.years")}` : null)}
        {row("phone", t("master.phone"), m.phone)}
      </div>

      <div className="action-bar">
        <button className="btn btn-lg btn-block" disabled={!m.phone} onClick={call}>
          <Icon name="phone" size={18} /> {t("masters.call")}
        </button>
      </div>
    </div>
  );
}
