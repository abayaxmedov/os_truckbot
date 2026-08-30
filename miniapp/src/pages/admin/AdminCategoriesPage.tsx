import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import type { Category } from "@/api/types";
import { Icon } from "@/components/Icon";
import { PageHeader } from "@/components/PageHeader";
import { Sheet } from "@/components/Sheet";
import { SkeletonList } from "@/components/Skeleton";
import { useToast } from "@/components/ui";
import { useApi } from "@/lib/useApi";
import { categoryIcon } from "@/lib/format";

export function AdminCategoriesPage() {
  const { t } = useTranslation();
  const toast = useToast();
  const { data, loading, reload } = useApi(() => api.getCategories(), []);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name_ru: "", name_uz: "", commission_override: "" });

  const flat = useMemo(() => {
    const out: Category[] = [];
    const walk = (l: Category[]) => l.forEach((c) => (out.push(c), walk(c.children)));
    walk(data || []);
    return out;
  }, [data]);

  const create = async () => {
    if (!form.name_ru.trim()) return;
    await api.createCategory({
      name_ru: form.name_ru.trim(),
      name_uz: form.name_uz.trim() || form.name_ru.trim(),
      commission_override: form.commission_override ? Number(form.commission_override) : null,
    });
    setOpen(false);
    setForm({ name_ru: "", name_uz: "", commission_override: "" });
    toast.show(t("profile.saved"));
    reload();
  };

  const remove = async (id: number) => {
    try {
      await api.deleteCategory(id);
      reload();
    } catch (e) {
      toast.show(e instanceof Error ? e.message : t("common.error"));
    }
  };

  return (
    <div>
      <PageHeader
        title={t("admin.categories")}
        action={<button className="fab" onClick={() => setOpen(true)}><Icon name="plus" size={20} strokeWidth={2.2} /></button>}
      />

      {loading ? (
        <SkeletonList count={6} />
      ) : (
        <div className="list">
          {flat.map((c) => (
            <div className="list-row" key={c.id} style={{ cursor: "default" }}>
              <span className="icon-chip" style={{ width: 34, height: 34 }}><Icon name={categoryIcon(c.slug)} size={17} /></span>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600 }}>{c.name_ru}</div>
                <div className="caption">{c.name_uz}{c.commission_override != null ? ` · ${c.commission_override}%` : ""}</div>
              </div>
              <button className="btn btn-sm btn-danger" onClick={() => remove(c.id)}><Icon name="trash" size={14} /></button>
            </div>
          ))}
        </div>
      )}

      <Sheet open={open} onClose={() => setOpen(false)} title={t("admin.addCategory")}>
        <div className="field"><label>RU</label><input className="input" value={form.name_ru} onChange={(e) => setForm((f) => ({ ...f, name_ru: e.target.value }))} /></div>
        <div className="field"><label>UZ</label><input className="input" value={form.name_uz} onChange={(e) => setForm((f) => ({ ...f, name_uz: e.target.value }))} /></div>
        <div className="field"><label>{t("seller.commission")} %</label><input className="input tnum" type="number" value={form.commission_override} onChange={(e) => setForm((f) => ({ ...f, commission_override: e.target.value }))} /></div>
        <button className="btn btn-block" onClick={create}>{t("common.add")}</button>
      </Sheet>
    </div>
  );
}
