import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import { Icon } from "@/components/Icon";
import { PageHeader } from "@/components/PageHeader";
import { SkeletonCards } from "@/components/Skeleton";
import { Empty, StatusBadge } from "@/components/ui";
import { useApi } from "@/lib/useApi";
import { formatMoney } from "@/lib/format";

export function OrdersPage() {
  const { t } = useTranslation();
  const nav = useNavigate();
  const { data, loading } = useApi(() => api.listOrders(1), []);

  return (
    <div>
      <PageHeader title={t("orders.title")} />
      {loading ? (
        <SkeletonCards count={3} height={78} />
      ) : (data?.items || []).length === 0 ? (
        <Empty icon="box" text={t("orders.empty")} />
      ) : (
        <div className="stack">
          {(data?.items || []).map((o) => (
            <div className="card card-pad" key={o.id} onClick={() => nav(`/orders/${o.id}`)} style={{ cursor: "pointer" }}>
              <div className="between">
                <span className="row" style={{ gap: 8 }}>
                  <span className="icon-chip" style={{ width: 32, height: 32 }}><Icon name="box" size={17} /></span>
                  <span className="bold">{t("orders.order")} #{o.id}</span>
                </span>
                <StatusBadge status={o.status_summary} />
              </div>
              <div className="between mt">
                <span className="caption">{o.items_count} {t("orders.items")} · {new Date(o.created_at).toLocaleDateString()}</span>
                <span className="bold tnum">{formatMoney(o.total)} {t("common.sum")}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
