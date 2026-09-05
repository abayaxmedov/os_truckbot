import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import type { ProductListItem } from "@/api/types";
import { mediaUrl } from "@/api/client";
import { CartControl } from "@/components/CartControl";
import { Placeholder } from "@/components/Placeholder";
import { countryLabel } from "@/lib/countries";
import { formatMoney } from "@/lib/format";
import { useAuth } from "@/store/auth";

export function ProductCard({ p }: { p: ProductListItem }) {
  const nav = useNavigate();
  const { t, i18n } = useTranslation();
  const isMaster = useAuth((s) => s.user?.is_master);
  const img = mediaUrl(p.image);
  const country = countryLabel(p.country, i18n.language);
  return (
    <div className="product-card" onClick={() => nav(`/product/${p.id}`)}>
      {img ? <img className="thumb" src={img} alt={p.name} loading="lazy" /> : <Placeholder />}
      {!p.in_stock && (
        <span className="badge badge-gray oos-tag">{t("product.outOfStock")}</span>
      )}
      <div className="pc-body">
        <div className="pc-name">{p.name}</div>
        {p.article && <div className="pc-meta">{t("product.article")}: {p.article}</div>}
        {country && <div className="pc-meta">{country}</div>}
        {isMaster && p.bonus > 0 && (
          <span className="badge badge-green tnum" style={{ alignSelf: "flex-start" }}>
            +{formatMoney(p.bonus)} {t("common.sum")}
          </span>
        )}
        <div className="between" style={{ marginTop: "auto", gap: 8 }}>
          <div className="pc-price tnum" style={{ marginTop: 0 }}>
            {formatMoney(p.price)} <small>{t("common.sum")}</small>
          </div>
          <CartControl productId={p.id} inStock={p.in_stock} stockQty={p.stock_qty} />
        </div>
      </div>
    </div>
  );
}
