import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import type { Category, ProductListItem, TruckBrand } from "@/api/types";
import { Icon } from "@/components/Icon";
import { ProductCard } from "@/components/ProductCard";
import { SelectSheet } from "@/components/SelectSheet";
import { SkeletonGrid } from "@/components/Skeleton";
import { Empty } from "@/components/ui";
import { haptic, openTelegramHandle } from "@/telegram/telegram";

const SORTS = ["new", "price_asc", "price_desc", "popular"] as const;

export function CatalogPage() {
  const { t } = useTranslation();
  const [params, setParams] = useSearchParams();

  const [q, setQ] = useState(params.get("q") || "");
  const [categoryId, setCategoryId] = useState<number | undefined>(
    params.get("category_id") ? Number(params.get("category_id")) : undefined,
  );
  const [brandId, setBrandId] = useState<number | undefined>(
    params.get("brand_id") ? Number(params.get("brand_id")) : undefined,
  );
  const [sort, setSort] = useState(params.get("sort") || "new");

  const [categories, setCategories] = useState<Category[]>([]);
  const [brands, setBrands] = useState<TruckBrand[]>([]);
  const [items, setItems] = useState<ProductListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [support, setSupport] = useState("");

  useEffect(() => {
    api.getCategories().then(setCategories).catch(() => {});
    api.getBrands().then(setBrands).catch(() => {});
    api.getPublicSettings().then((s) => setSupport(s.support_telegram || "")).catch(() => {});
  }, []);

  useEffect(() => setPage(1), [q, categoryId, brandId, sort]);

  useEffect(() => {
    let active = true;
    setLoading(true);
    api
      .listProducts({ q, category_id: categoryId, brand_id: brandId, sort, page, page_size: 20 })
      .then((res) => {
        if (!active) return;
        setItems((prev) => (page === 1 ? res.items : [...prev, ...res.items]));
        setTotal(res.total);
      })
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [q, categoryId, brandId, sort, page]);

  const flatCategories = useMemo(() => {
    const out: Category[] = [];
    const walk = (list: Category[]) => list.forEach((c) => (out.push(c), walk(c.children)));
    walk(categories);
    return out;
  }, [categories]);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const p = new URLSearchParams(params);
    if (q) p.set("q", q);
    else p.delete("q");
    setParams(p, { replace: true });
  };

  return (
    <div>
      <form className="searchbar" onSubmit={submit}>
        <Icon name="search" size={19} className="ic" />
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder={t("home.searchPlaceholder")}
          enterKeyHint="search"
        />
        {q && (
          <button type="button" className="ic" onClick={() => setQ("")} style={{ background: "none", border: 0, color: "var(--muted)", cursor: "pointer", padding: 0 }}>
            <Icon name="x" size={18} />
          </button>
        )}
      </form>

      <div className="chips mb">
        <div className={`chip ${!categoryId ? "active" : ""}`} onClick={() => setCategoryId(undefined)}>
          {t("common.all")}
        </div>
        {flatCategories.map((c) => (
          <div
            key={c.id}
            className={`chip ${categoryId === c.id ? "active" : ""}`}
            onClick={() => setCategoryId(categoryId === c.id ? undefined : c.id)}
          >
            {c.name}
          </div>
        ))}
      </div>

      <div className="row mb" style={{ gap: 10 }}>
        <SelectSheet
          icon="truck"
          title={t("catalog.brand")}
          placeholder={`${t("catalog.brand")}: ${t("common.all")}`}
          value={brandId ?? ""}
          onChange={(v) => setBrandId(v === "" ? undefined : Number(v))}
          options={[
            { value: "" as const, label: t("common.all") },
            ...brands.map((b) => ({ value: b.id, label: b.name })),
          ]}
        />
        <SelectSheet
          icon="sliders"
          title={t("catalog.sort")}
          value={sort}
          onChange={(v) => setSort(String(v))}
          options={SORTS.map((s) => ({
            value: s as string,
            label: t(`catalog.sort${s === "new" ? "New" : s === "price_asc" ? "PriceAsc" : s === "price_desc" ? "PriceDesc" : "Popular"}`),
          }))}
        />
      </div>

      {loading && page === 1 ? (
        <SkeletonGrid count={6} />
      ) : items.length === 0 ? (
        support ? (
          <div className="empty-wrap">
            <span className="icon-chip" style={{ width: 60, height: 60, background: "var(--accent-tint)", color: "var(--accent)" }}>
              <Icon name="search" size={28} />
            </span>
            <div className="bold" style={{ fontSize: 17, marginTop: 12 }}>{t("catalog.notFoundTitle")}</div>
            <div className="muted small" style={{ textAlign: "center", maxWidth: 280, marginTop: 4 }}>{t("catalog.notFoundText")}</div>
            <button className="btn btn-lg mt" style={{ minWidth: 240 }} onClick={() => { haptic("light"); openTelegramHandle(support); }}>
              <Icon name="message" size={18} /> {t("catalog.writeAdmin")}
            </button>
            <div className="caption mt-sm">@{support}</div>
          </div>
        ) : (
          <Empty icon="search" text={t("common.empty")} />
        )
      ) : (
        <>
          <div className="grid">
            {items.map((p) => (
              <ProductCard key={p.id} p={p} />
            ))}
          </div>
          {items.length < total && (
            <button className="btn btn-secondary btn-block mt" disabled={loading} onClick={() => setPage((p) => p + 1)}>
              {loading ? t("common.loading") : "＋"}
            </button>
          )}
        </>
      )}
    </div>
  );
}
