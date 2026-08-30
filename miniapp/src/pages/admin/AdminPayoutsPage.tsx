import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import type { AdminPayout } from "@/api/types";
import { Icon } from "@/components/Icon";
import { PageHeader } from "@/components/PageHeader";
import { Segmented } from "@/components/Segmented";
import { SkeletonCards } from "@/components/Skeleton";
import { Empty, StatusBadge, useToast } from "@/components/ui";
import { formatMoney } from "@/lib/format";

export function AdminPayoutsPage() {
  const { t } = useTranslation();
  const toast = useToast();
  const [status, setStatus] = useState("pending");
  const [items, setItems] = useState<AdminPayout[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    api.getAdminPayouts(status).then(setItems).finally(() => setLoading(false));
  };
  useEffect(load, [status]);

  const act = async (id: number, action: "paid" | "rejected") => {
    await api.updatePayout(id, action);
    toast.show(t("profile.saved"));
    load();
  };

  const run = async () => {
    const r = await api.runPayouts();
    toast.show(`${t("admin.runPayouts")}: ${r.detail}`);
    load();
  };

  return (
    <div>
      <PageHeader
        title={t("admin.payouts")}
        action={<button className="btn btn-sm btn-secondary" onClick={run}><Icon name="card" size={15} /> {t("admin.runPayouts")}</button>}
      />
      <div className="mb">
        <Segmented
          value={status}
          onChange={setStatus}
          options={[
            { value: "pending", label: t("status.pending") },
            { value: "paid", label: t("status.paid") },
            { value: "rejected", label: t("admin.reject") },
          ]}
        />
      </div>

      {loading ? (
        <SkeletonCards count={3} height={100} />
      ) : items.length === 0 ? (
        <Empty icon="card" text={t("admin.noPayouts")} />
      ) : (
        <div className="stack">
          {items.map((p) => (
            <div className="card card-pad" key={p.id}>
              <div className="between">
                <span className="row bold" style={{ gap: 8 }}><Icon name="wrench" size={16} /> {p.master_name}</span>
                <StatusBadge status={p.status} />
              </div>
              <div className="caption mt-sm">{p.phone}</div>
              <div className="between mt">
                <span className="bold tnum" style={{ fontSize: 18 }}>{formatMoney(p.amount)} {t("common.sum")}</span>
                <span className="caption tnum">{t("admin.card")}: {p.card_number || "—"}</span>
              </div>
              {p.status === "pending" && (
                <div className="row mt" style={{ gap: 8 }}>
                  <button className="btn btn-sm btn-block" onClick={() => act(p.id, "paid")}><Icon name="check" size={15} /> {t("admin.markPaid")}</button>
                  <button className="btn btn-sm btn-danger btn-block" onClick={() => act(p.id, "rejected")}><Icon name="x" size={15} /> {t("admin.reject")}</button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
