import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import { mediaUrl } from "@/api/client";
import { Icon } from "@/components/Icon";
import { PageHeader } from "@/components/PageHeader";
import { Placeholder } from "@/components/Placeholder";
import { SkeletonList } from "@/components/Skeleton";
import { Empty } from "@/components/ui";
import { useApi } from "@/lib/useApi";
import { formatMoney, statusTone } from "@/lib/format";

export function SellerProductsPage() {
  const { t } = useTranslation();
  const nav = useNavigate();
  const { data, loading } = useApi(() => api.getSellerProducts(1), []);

  return (
    <div>
      <PageHeader
        title={t("seller.products")}
        action={<button className="fab" onClick={() => nav("/seller/products/new")}><Icon name="plus" size={20} strokeWidth={2.2} /></button>}
      />

      {loading ? (
        <SkeletonList count={5} />
      ) : (data?.items || []).length === 0 ? (
        <Empty icon="box" text={t("common.empty")} />
      ) : (
        <div className="list">
          {(data?.items || []).map((p) => (
            <button className="list-row" key={p.id} onClick={() => nav(`/seller/products/${p.id}/edit`)}>
              <span style={{ width: 44, height: 44, borderRadius: 10, overflow: "hidden", flex: "none" }}>
                {p.image ? <img src={mediaUrl(p.image)} style={{ width: 44, height: 44, objectFit: "cover" }} /> : <Placeholder size={20} />}
              </span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div className="small" style={{ fontWeight: 600, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{p.name}</div>
                <div className="caption tnum">{formatMoney(p.price)} {t("common.sum")} · {p.stock_qty} {t("common.all").toLowerCase()}</div>
              </div>
              <span className={`badge badge-${statusTone(p.status)}`}>{t(`seller.moderation${p.status.charAt(0).toUpperCase() + p.status.slice(1)}`, { defaultValue: p.status })}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
