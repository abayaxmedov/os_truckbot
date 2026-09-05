import { useState } from "react";
import { Navigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import { mediaUrl } from "@/api/client";
import { Icon } from "@/components/Icon";
import { MasterRegisterForm } from "@/components/MasterRegisterForm";
import { PageHeader } from "@/components/PageHeader";
import { Loader, StatusBadge } from "@/components/ui";
import { useApi } from "@/lib/useApi";
import { formatMoney } from "@/lib/format";
import { labelsFor, SPECIALIZATIONS, TRUCKS } from "@/lib/masterOptions";
import { useAuth } from "@/store/auth";

export function MasterCabinet() {
  const user = useAuth((s) => s.user);

  // The cabinet is only for masters. Role is chosen once at first run, so an
  // onboarded buyer who reaches /master by URL is sent home (no "become master").
  if (!user?.is_master) {
    return <Navigate to="/" replace />;
  }
  return <MasterHome />;
}

function MasterHome() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const [editing, setEditing] = useState(false);
  const master = useApi(() => api.getMaster(), [editing]);
  const txns = useApi(() => api.getMasterTransactions(), []);
  const payouts = useApi(() => api.getMasterPayouts(), []);

  if (editing) {
    return (
      <div>
        <PageHeader
          title={t("master.editProfile")}
          action={
            <button className="btn btn-sm btn-secondary" onClick={() => setEditing(false)}>
              <Icon name="chevron" size={15} style={{ transform: "rotate(180deg)" }} /> {t("common.back")}
            </button>
          }
        />
        <MasterRegisterForm onDone={() => setEditing(false)} />
      </div>
    );
  }

  if (master.loading || !master.data) return <Loader />;
  const m = master.data;
  const truckLabels = labelsFor(TRUCKS, m.trucks, lang);
  const specLabels = labelsFor(SPECIALIZATIONS, m.specializations, lang);
  const fullName = [m.first_name, m.last_name].filter(Boolean).join(" ").trim();

  return (
    <div>
      <PageHeader title={t("master.cabinet")} />

      {/* Service profile summary */}
      <div className="card card-pad mb">
        <div className="row" style={{ gap: 12, alignItems: "center" }}>
          {m.photo ? (
            <img src={mediaUrl(m.photo)} style={{ width: 56, height: 56, borderRadius: "50%", objectFit: "cover", flex: "none" }} />
          ) : (
            <span className="icon-chip" style={{ width: 56, height: 56, flex: "none" }}><Icon name="user" size={26} /></span>
          )}
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="row" style={{ gap: 6, flexWrap: "wrap" }}>
              <span className="bold" style={{ fontSize: 16 }}>{fullName || t("master.cabinet")}</span>
              {m.is_verified && (
                <span className="badge badge-green" style={{ gap: 3 }}><Icon name="check" size={12} strokeWidth={3} /> {t("master.verified")}</span>
              )}
            </div>
            <div className="caption">
              {m.experience_years ? `${t("master.experience")}: ${m.experience_years} · ` : ""}
              {m.is_24_7 ? "🚨 24/7" : m.work_hours || ""}
            </div>
          </div>
          <button className="btn btn-sm btn-secondary" style={{ flex: "none" }} onClick={() => setEditing(true)}>
            <Icon name="edit" size={15} /> {t("common.edit")}
          </button>
        </div>

        {truckLabels.length > 0 && (
          <div className="chip-wrap mt">
            {truckLabels.map((l) => <span key={l} className="chip chip-static">🚛 {l}</span>)}
          </div>
        )}
        {specLabels.length > 0 && (
          <div className="chip-wrap mt-sm">
            {specLabels.map((l) => <span key={l} className="chip chip-static">🛠 {l}</span>)}
          </div>
        )}
        {(m.price_call != null || m.price_diagnostics != null || m.price_repair_note) && (
          <div className="mt" style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {m.price_call != null && <div className="small between"><span className="muted">{t("master.priceCall")}</span><b className="tnum">{formatMoney(m.price_call)} {t("common.sum")}</b></div>}
            {m.price_diagnostics != null && <div className="small between"><span className="muted">{t("master.priceDiagnostics")}</span><b className="tnum">{formatMoney(m.price_diagnostics)} {t("common.sum")}</b></div>}
            {m.price_repair_note && <div className="small between"><span className="muted">{t("master.priceRepair")}</span><b>{m.price_repair_note}</b></div>}
          </div>
        )}
        {(truckLabels.length === 0 && specLabels.length === 0) && (
          <button className="btn btn-block btn-secondary mt" onClick={() => setEditing(true)}>
            <Icon name="edit" size={16} /> {t("master.fillProfile")}
          </button>
        )}
      </div>

      <div className="card card-pad mb" style={{ background: "linear-gradient(120deg,var(--brand-700),var(--brand-500))", color: "#fff", border: 0 }}>
        <div className="caption" style={{ color: "rgba(255,255,255,.8)" }}>{t("master.available")}</div>
        <div className="tnum" style={{ fontSize: 32, fontWeight: 800, letterSpacing: "-0.02em" }}>
          {formatMoney(m.balance)} <span style={{ fontSize: 15, opacity: 0.85 }}>{t("common.sum")}</span>
        </div>
        <div className="row mt" style={{ gap: 16, opacity: 0.92, flexWrap: "wrap" }}>
          <span className="small">{t("master.pending")}: <b className="tnum">{formatMoney(m.pending)}</b></span>
          <span className="small">{t("master.totalEarned")}: <b className="tnum">{formatMoney(m.total_earned)}</b></span>
        </div>
      </div>

      <div className="card card-pad mb row" style={{ gap: 10 }}>
        <span className="icon-chip" style={{ width: 36, height: 36 }}><Icon name="card" size={18} /></span>
        <div style={{ flex: 1 }}>
          <div className="small" style={{ fontWeight: 600 }}>
            {t("master.nextPayout")}: {m.next_payout_at ? new Date(m.next_payout_at).toLocaleDateString() : "—"}
          </div>
          <div className="caption">{t("master.payoutInfo")}</div>
        </div>
      </div>

      <div className="section-title">{t("master.transactions")}</div>
      {txns.loading ? (
        <Loader />
      ) : (txns.data || []).length === 0 ? (
        <div className="card card-pad caption center">{t("master.noData")}</div>
      ) : (
        <div className="list">
          {(txns.data || []).map((tx) => (
            <div className="list-row" key={tx.id} style={{ cursor: "default" }}>
              <span className="icon-chip" style={{ width: 32, height: 32 }}><Icon name="gift" size={16} /></span>
              <div style={{ flex: 1 }}>
                <div className="small" style={{ fontWeight: 600 }}>+{formatMoney(tx.amount)} {t("common.sum")}</div>
                <div className="caption">{tx.note} · {new Date(tx.created_at).toLocaleDateString()}</div>
              </div>
              <StatusBadge status={tx.status} />
            </div>
          ))}
        </div>
      )}

      {(payouts.data || []).length > 0 && (
        <>
          <div className="section-title">{t("master.payouts")}</div>
          <div className="list">
            {(payouts.data || []).map((p) => (
              <div className="list-row" key={p.id} style={{ cursor: "default" }}>
                <span className="icon-chip" style={{ width: 32, height: 32 }}><Icon name="card" size={16} /></span>
                <div style={{ flex: 1 }}>
                  <div className="small tnum" style={{ fontWeight: 600 }}>{formatMoney(p.amount)} {t("common.sum")}</div>
                  <div className="caption">{new Date(p.created_at).toLocaleDateString()}</div>
                </div>
                <StatusBadge status={p.status} />
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
