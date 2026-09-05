import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import type { MasterPublic } from "@/api/types";
import { mediaUrl } from "@/api/client";
import { Icon } from "@/components/Icon";
import { formatMoney } from "@/lib/format";
import { labelsFor, SPECIALIZATIONS, TRUCKS } from "@/lib/masterOptions";

export function MasterCard({ m, dist }: { m: MasterPublic; dist?: { distance_km: number; eta_min: number } }) {
  const nav = useNavigate();
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const trucks = labelsFor(TRUCKS, m.trucks, lang);
  const specs = labelsFor(SPECIALIZATIONS, m.specializations, lang);

  return (
    <div className="card card-pad master-card" onClick={() => nav(`/masters/${m.id}`)}>
      <div className="row" style={{ gap: 12, alignItems: "flex-start" }}>
        {m.photo ? (
          <img src={mediaUrl(m.photo)} className="master-ava" alt={m.name} />
        ) : (
          <span className="icon-chip master-ava" style={{ flex: "none" }}><Icon name="user" size={24} /></span>
        )}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div className="row" style={{ gap: 6, flexWrap: "wrap" }}>
            <span className="bold" style={{ fontSize: 15.5 }}>{m.name || "—"}</span>
            {m.is_verified && (
              <span className="badge badge-green" style={{ gap: 3 }}><Icon name="check" size={11} strokeWidth={3} /> {t("master.verified")}</span>
            )}
          </div>
          <div className="caption" style={{ marginTop: 2 }}>
            {m.experience_years ? `${m.experience_years} ${t("master.years")}` : ""}
            {m.experience_years && (m.is_24_7 || m.work_hours) ? " · " : ""}
            {m.is_24_7 ? "🚨 24/7" : m.work_hours}
          </div>
          {m.regions && <div className="caption row" style={{ gap: 4, marginTop: 2 }}><Icon name="pin" size={12} /> {m.regions}</div>}
          {dist && (
            <div className="row" style={{ gap: 4, marginTop: 3, color: "var(--brand)", fontWeight: 700, fontSize: 12.5 }}>
              <Icon name="pin" size={12} /> {dist.distance_km} {t("masters.km")} · ~{dist.eta_min} {t("masters.min")}
            </div>
          )}
        </div>
        <Icon name="chevron" size={18} className="chevron" style={{ flex: "none" }} />
      </div>

      {trucks.length > 0 && (
        <div className="master-tags mt-sm">
          {trucks.slice(0, 4).map((l) => <span key={l} className="mtag mtag-truck">{l}</span>)}
        </div>
      )}
      {specs.length > 0 && (
        <div className="master-tags mt-sm">
          {specs.slice(0, 4).map((l) => <span key={l} className="mtag">{l}</span>)}
          {specs.length > 4 && <span className="mtag">+{specs.length - 4}</span>}
        </div>
      )}

      {m.price_call != null && (
        <div className="between mt" style={{ alignItems: "center" }}>
          <span className="caption">{t("master.priceCall")}</span>
          <span className="bold tnum">{formatMoney(m.price_call)} {t("common.sum")}</span>
        </div>
      )}
    </div>
  );
}
