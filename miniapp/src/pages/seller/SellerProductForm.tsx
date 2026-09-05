import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import type { Category, Product, TruckBrand } from "@/api/types";
import { mediaUrl } from "@/api/client";
import { Icon } from "@/components/Icon";
import { PageHeader } from "@/components/PageHeader";
import { SelectSheet } from "@/components/SelectSheet";
import { Loader, useToast } from "@/components/ui";
import { COUNTRIES } from "@/lib/countries";

const EMPTY = {
  category_id: 0, name_ru: "", name_uz: "", article: "", oem_number: "", part_brand: "",
  country: "", engine: "", description_ru: "", description_uz: "", price: 0, stock_qty: 0, warranty: "",
};

export function SellerProductForm() {
  const { id } = useParams();
  const editingId = id ? Number(id) : null;
  const { t, i18n } = useTranslation();
  const nav = useNavigate();
  const toast = useToast();
  const fileRef = useRef<HTMLInputElement>(null);

  const [categories, setCategories] = useState<Category[]>([]);
  const [brands, setBrands] = useState<TruckBrand[]>([]);
  const [form, setForm] = useState({ ...EMPTY });
  const [brandId, setBrandId] = useState<number | "">("");
  const [modelId, setModelId] = useState<number | "">("");
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    Promise.all([api.getCategories(), api.getBrands()]).then(([cats, brs]) => {
      setCategories(cats);
      setBrands(brs);
    });
  }, []);

  useEffect(() => {
    if (!editingId) {
      setLoading(false);
      return;
    }
    api.getProduct(editingId).then((p) => {
      setProduct(p);
      setForm({
        category_id: p.category_id, name_ru: p.name_ru, name_uz: p.name_uz, article: p.article,
        oem_number: p.oem_number, part_brand: p.part_brand, country: p.country, engine: p.engine,
        description_ru: p.description_ru, description_uz: p.description_uz, price: p.price,
        stock_qty: p.stock_qty, warranty: p.warranty,
      });
      if (p.vehicles[0]) {
        setBrandId(p.vehicles[0].brand_id);
        setModelId(p.vehicles[0].model_id ?? "");
      }
      setLoading(false);
    });
  }, [editingId]);

  const flatCats = useMemo(() => {
    const out: Category[] = [];
    const walk = (l: Category[]) => l.forEach((c) => (out.push(c), walk(c.children)));
    walk(categories);
    return out;
  }, [categories]);

  const models = useMemo(() => brands.find((b) => b.id === brandId)?.models || [], [brands, brandId]);
  const set = (k: string, v: string | number) => setForm((f) => ({ ...f, [k]: v }));

  const save = async () => {
    if (!form.category_id || !form.name_ru.trim()) {
      toast.show(t("checkout.required"));
      return;
    }
    setBusy(true);
    try {
      const payload = {
        ...form, price: Number(form.price), stock_qty: Number(form.stock_qty),
        vehicles: brandId ? [{ truck_brand_id: Number(brandId), truck_model_id: modelId ? Number(modelId) : null }] : [],
      };
      if (editingId) {
        await api.updateSellerProduct(editingId, payload);
        toast.show(t("profile.saved"));
        nav(-1);
      } else {
        const created = await api.createSellerProduct(payload);
        toast.show(t("profile.saved"));
        nav(`/seller/products/${created.id}/edit`, { replace: true });
      }
    } catch (e) {
      toast.show(e instanceof Error ? e.message : t("common.error"));
    } finally {
      setBusy(false);
    }
  };

  const onUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !editingId) return;
    setProduct(await api.uploadProductImage(editingId, file));
    toast.show(t("profile.saved"));
  };

  if (loading) return <Loader />;

  return (
    <div>
      <PageHeader title={editingId ? t("seller.editProduct") : t("seller.newProduct")} />

      <div className="card card-pad mb">
        <div className="field">
          <label>{t("catalog.category")} *</label>
          <SelectSheet
            icon="grid"
            title={t("catalog.category")}
            value={form.category_id || ""}
            onChange={(v) => set("category_id", Number(v) || 0)}
            options={flatCats.map((c) => ({ value: c.id, label: c.name }))}
          />
        </div>
        <div className="row" style={{ gap: 10 }}>
          <div className="field" style={{ flex: 1, minWidth: 0 }}>
            <label>{t("catalog.brand")}</label>
            <SelectSheet
              icon="truck"
              title={t("catalog.brand")}
              value={brandId}
              onChange={(v) => { setBrandId(v === "" ? "" : Number(v)); setModelId(""); }}
              options={[{ value: "" as const, label: "—" }, ...brands.map((b) => ({ value: b.id, label: b.name }))]}
            />
          </div>
          <div className="field" style={{ flex: 1, minWidth: 0 }}>
            <label>{t("catalog.model")}</label>
            <SelectSheet
              icon="settings"
              title={t("catalog.model")}
              value={modelId}
              onChange={(v) => setModelId(v === "" ? "" : Number(v))}
              options={[{ value: "" as const, label: "—" }, ...models.map((m) => ({ value: m.id, label: m.name }))]}
            />
          </div>
        </div>
        <div className="field" style={{ marginBottom: 0 }}><label>{t("seller.products")} (RU) *</label><input className="input" value={form.name_ru} onChange={(e) => set("name_ru", e.target.value)} /></div>
      </div>

      <div className="card card-pad mb">
        <div className="field"><label>{t("seller.products")} (UZ)</label><input className="input" value={form.name_uz} onChange={(e) => set("name_uz", e.target.value)} /></div>
        <div className="row" style={{ gap: 10 }}>
          <div className="field" style={{ flex: 1 }}><label>{t("product.article")}</label><input className="input" value={form.article} onChange={(e) => set("article", e.target.value)} /></div>
          <div className="field" style={{ flex: 1 }}><label>{t("product.oem")}</label><input className="input" value={form.oem_number} onChange={(e) => set("oem_number", e.target.value)} /></div>
        </div>
        <div className="row" style={{ gap: 10 }}>
          <div className="field" style={{ flex: 1 }}><label>{t("product.partBrand")}</label><input className="input" value={form.part_brand} onChange={(e) => set("part_brand", e.target.value)} /></div>
          <div className="field" style={{ flex: 1 }}><label>{t("catalog.engine")}</label><input className="input" value={form.engine} onChange={(e) => set("engine", e.target.value)} /></div>
        </div>
        <div className="field">
          <label>{t("product.country")}</label>
          <SelectSheet
            icon="truck"
            title={t("product.country")}
            placeholder="—"
            value={form.country}
            onChange={(v) => set("country", String(v))}
            options={COUNTRIES.map((c) => ({ value: c.code, label: `${c.flag} ${i18n.language === "uz" ? c.uz : c.ru}` }))}
          />
        </div>
        <div className="row" style={{ gap: 10 }}>
          <div className="field" style={{ flex: 1 }}><label>{t("cart.total")} *</label><input className="input tnum" type="number" inputMode="numeric" value={form.price} onChange={(e) => set("price", e.target.value)} /></div>
          <div className="field" style={{ flex: 1 }}><label>{t("product.inStock")}</label><input className="input tnum" type="number" inputMode="numeric" value={form.stock_qty} onChange={(e) => set("stock_qty", e.target.value)} /></div>
        </div>
        <div className="field"><label>{t("product.warranty")}</label><input className="input" value={form.warranty} onChange={(e) => set("warranty", e.target.value)} /></div>
        <div className="field"><label>{t("product.description")} (RU)</label><textarea className="textarea" value={form.description_ru} onChange={(e) => set("description_ru", e.target.value)} /></div>
        <div className="field" style={{ marginBottom: 0 }}><label>{t("product.description")} (UZ)</label><textarea className="textarea" value={form.description_uz} onChange={(e) => set("description_uz", e.target.value)} /></div>
      </div>

      {editingId && (
        <>
          <div className="section-title">{t("seller.photos")}</div>
          <div className="row wrap mb" style={{ gap: 10 }}>
            {product?.images.map((im) => (
              <img key={im.id} src={mediaUrl(im.url)} style={{ width: 64, height: 64, borderRadius: 12, objectFit: "cover" }} />
            ))}
            <button className="card" style={{ width: 64, height: 64, display: "flex", alignItems: "center", justifyContent: "center", color: "var(--brand)", borderStyle: "dashed", borderColor: "var(--brand)", cursor: "pointer" }} onClick={() => fileRef.current?.click()}>
              <Icon name="camera" size={22} />
            </button>
          </div>
          <input ref={fileRef} type="file" accept="image/*" style={{ display: "none" }} onChange={onUpload} />
        </>
      )}

      <div className="action-bar">
        <button className="btn btn-lg btn-block" disabled={busy} onClick={save}>
          {busy ? <span className="spin" /> : <Icon name="check" size={18} />} {t("common.save")}
        </button>
        {editingId && (
          <button className="btn btn-danger btn-block" onClick={async () => { await api.deleteSellerProduct(editingId); nav("/seller/products", { replace: true }); }}>
            <Icon name="trash" size={17} /> {t("common.delete")}
          </button>
        )}
      </div>
    </div>
  );
}
