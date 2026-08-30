import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import type { ProductListItem } from "@/api/types";
import { mediaUrl } from "@/api/client";
import { Placeholder } from "@/components/Placeholder";
import { formatMoney } from "@/lib/format";
import { useAuth } from "@/store/auth";

export function ProductCard({ p }: { p: ProductListItem }) {
  const nav = useNavigate();
  const { t } = useTranslation();
  const isMaster = useAuth((s) => s.user?.is_master);
  const img = mediaUrl(p.image);
  return (
    <div className="product-card" onClick={() => nav(`/product/${p.id}`)}>
      {img ? <img className="thumb" src={img} alt={p.name} loading="lazy" /> : <Placeholder />}
      {!p.in_stock && (
        <span className="badge badge-gray oos-tag">{t("product.outOfStock")}</span>
      )}
      <div className="pc-body">
        <div className="pc-name">{p.name}</div>
        {p.article && <div className="pc-meta">{t("product.article")}: {p.article}</div>}
        <div className="pc-price tnum">
          {formatMoney(p.price)} <small>{t("common.sum")}</small>
        </div>
        {isMaster && p.bonus > 0 && (
          <span className="badge badge-green tnum" style={{ alignSelf: "flex-start" }}>
            +{formatMoney(p.bonus)} {t("common.sum")}
          </span>
        )}
      </div>
    </div>
  );
}
