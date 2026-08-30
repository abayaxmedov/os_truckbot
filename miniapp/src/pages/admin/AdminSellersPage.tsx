import { useState } from "react";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import type { AdminSeller } from "@/api/types";
import { Icon } from "@/components/Icon";
import { PageHeader } from "@/components/PageHeader";
import { Sheet } from "@/components/Sheet";
import { SkeletonCards } from "@/components/Skeleton";
import { Empty, useToast } from "@/components/ui";
import { useApi } from "@/lib/useApi";
import { statusTone } from "@/lib/format";

export function AdminSellersPage() {
  const { t } = useTranslation();
  const toast = useToast();
  const { data, loading, reload } = useApi(() => api.getAdminSellers(), []);
  const [editing, setEditing] = useState<AdminSeller | null>(null);
  const [commission, setCommission] = useState("");

  const toggle = async (s: AdminSeller) => {
    await api.setSellerStatus(s.id, s.status === "blocked" ? "active" : "blocked");
    reload();
  };

  const saveCommission = async () => {
    if (!editing) return;
    await api.setSellerCommission(editing.id, commission === "" ? null : Number(commission));
    setEditing(null);
    setCommission("");
    toast.show(t("profile.saved"));
    reload();
  };

  return (
    <div>
      <PageHeader title={t("admin.sellers")} />
      {loading ? (
        <SkeletonCards count={3} height={110} />
      ) : (data || []).length === 0 ? (
        <Empty icon="store" text={t("common.empty")} />
      ) : (
        <div className="stack">
          {(data || []).map((s) => (
            <div className="card card-pad" key={s.id}>
              <div className="between">
                <span className="row bold" style={{ gap: 8 }}><Icon name="store" size={17} /> {s.shop_name}</span>
                <span className={`badge badge-${statusTone(s.status)}`}>{t(`status.${s.status}`, { defaultValue: s.status })}</span>
              </div>
              <div className="caption mt-sm">
                ★ {s.rating.toFixed(1)} · {s.products_count} {t("admin.products").toLowerCase()} · {s.orders_count} {t("seller.orders").toLowerCase()}
                {s.commission_override != null && ` · ${s.commission_override}%`}
              </div>
              <div className="row mt" style={{ gap: 8 }}>
                <button className="btn btn-sm btn-secondary" onClick={() => { setEditing(s); setCommission(s.commission_override?.toString() ?? ""); }}>
                  <Icon name="percent" size={14} /> {t("seller.commission")}
                </button>
                <button className={`btn btn-sm ${s.status === "blocked" ? "btn-secondary" : "btn-danger"}`} onClick={() => toggle(s)}>
                  {s.status === "blocked" ? t("admin.unblock") : t("admin.block")}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Sheet open={!!editing} onClose={() => setEditing(null)} title={`${editing?.shop_name ?? ""} · ${t("seller.commission")}`}>
        <div className="field">
          <label>{t("admin.defaultCommission")}</label>
          <input className="input tnum" type="number" inputMode="decimal" value={commission} onChange={(e) => setCommission(e.target.value)} placeholder={t("common.all")} />
        </div>
        <button className="btn btn-block" onClick={saveCommission}>{t("common.save")}</button>
      </Sheet>
    </div>
  );
}
