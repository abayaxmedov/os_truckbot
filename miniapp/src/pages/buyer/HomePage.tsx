import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import { mediaUrl } from "@/api/client";
import { BrandLogo } from "@/components/BrandLogo";
import { Icon } from "@/components/Icon";
import { Logo } from "@/components/Logo";
import { ProductCard } from "@/components/ProductCard";
import { SkeletonGrid } from "@/components/Skeleton";
import { useApi } from "@/lib/useApi";
import { categoryIcon } from "@/lib/format";

export function HomePage() {
  const { t } = useTranslation();
  const nav = useNavigate();
  const [q, setQ] = useState("");

  const banners = useApi(() => api.getBanners(), []);
  const categories = useApi(() => api.getCategories(), []);
  const brands = useApi(() => api.getBrands(), []);
  const popular = useApi(() => api.getPopular(8), []);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (q.trim()) nav(`/catalog?q=${encodeURIComponent(q.trim())}`);
  };

  const banner = banners.data?.[0];

  return (
    <div>
      <div className="center" style={{ padding: "2px 0 12px" }}>
        <Logo height={32} />
      </div>

      <form className="searchbar" onSubmit={submit}>
        <Icon name="search" size={19} className="ic" />
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder={t("home.searchPlaceholder")}
          enterKeyHint="search"
        />
      </form>

      {banner ? (
        <div className="banner mb" onClick={() => banner.target && nav(banner.target)}>
          <img src={mediaUrl(banner.image)} alt={banner.title} />
        </div>
      ) : (
        <div className="hero mb" style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
          <div>
            <h2>{t("home.title")}</h2>
            <p>MAN · Volvo · DAF · Scania · Mercedes · Renault · Iveco</p>
          </div>
          <Logo variant="white" mark height={68} />
        </div>
      )}

      {brands.data && brands.data.length > 0 && (
        <>
          <div className="section-head">
            <span className="sh-title">{t("home.brands")}</span>
          </div>
          <div className="chips">
            {brands.data.map((b) => (
              <BrandLogo key={b.id} name={b.name} slug={b.slug} onClick={() => nav(`/catalog?brand_id=${b.id}`)} />
            ))}
          </div>
        </>
      )}

      <div className="section-head">
        <span className="sh-title">{t("home.categories")}</span>
      </div>
      {categories.loading ? (
        <div className="cat-grid">
          {Array.from({ length: 8 }).map((_, i) => (
            <div className="skel" key={i} style={{ height: 60, borderRadius: 14 }} />
          ))}
        </div>
      ) : (
        <div className="cat-grid">
          {(categories.data || []).map((c) => (
            <div key={c.id} className="cat-tile" onClick={() => nav(`/catalog?category_id=${c.id}`)}>
              <span className="icon-chip" style={{ width: 40, height: 40 }}>
                <Icon name={categoryIcon(c.slug)} size={21} />
              </span>
              <span style={{ lineHeight: 1.2 }}>{c.name}</span>
            </div>
          ))}
        </div>
      )}

      <div className="section-head">
        <span className="sh-title">{t("home.popular")}</span>
        <span className="sh-link" onClick={() => nav("/catalog?sort=popular")}>
          {t("common.all")} ›
        </span>
      </div>
      {popular.loading ? (
        <SkeletonGrid count={4} />
      ) : (
        <div className="grid">
          {(popular.data || []).map((p) => (
            <ProductCard key={p.id} p={p} />
          ))}
        </div>
      )}
    </div>
  );
}
