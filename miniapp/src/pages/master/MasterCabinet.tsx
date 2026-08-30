import { useTranslation } from "react-i18next";

import * as api from "@/api";
import { Icon } from "@/components/Icon";
import { MasterRegisterForm } from "@/components/MasterRegisterForm";
import { PageHeader } from "@/components/PageHeader";
import { Loader, StatusBadge } from "@/components/ui";
import { useApi } from "@/lib/useApi";
import { formatMoney } from "@/lib/format";
import { useAuth } from "@/store/auth";

export function MasterCabinet() {
  const { t } = useTranslation();
  const user = useAuth((s) => s.user);

  if (!user?.is_master) {
    return (
      <div>
        <PageHeader title={t("master.register")} />
        <MasterRegisterForm />
      </div>
    );
  }
  return <MasterHome />;
}

function MasterHome() {
  const { t } = useTranslation();
  const master = useApi(() => api.getMaster(), []);
  const txns = useApi(() => api.getMasterTransactions(), []);
  const payouts = useApi(() => api.getMasterPayouts(), []);

  if (master.loading || !master.data) return <Loader />;
  const m = master.data;

  return (
    <div>
      <PageHeader title={t("master.cabinet")} />

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
