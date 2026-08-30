import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import type { AnalogGroup } from "@/api/types";
import { Icon } from "@/components/Icon";
import { PageHeader } from "@/components/PageHeader";
import { Sheet } from "@/components/Sheet";
import { SkeletonCards } from "@/components/Skeleton";
import { useToast } from "@/components/ui";

interface NumRow {
  number: string;
  brand: string;
  is_original: boolean;
}

export function AdminAnalogsPage() {
  const { t } = useTranslation();
  const toast = useToast();
  const [query, setQuery] = useState("");
  const [groups, setGroups] = useState<AnalogGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [rows, setRows] = useState<NumRow[]>([{ number: "", brand: "", is_original: true }]);

  const load = () => {
    setLoading(true);
    api.listAnalogs(query || undefined).then(setGroups).finally(() => setLoading(false));
  };
  useEffect(load, []);

  const createGroup = async () => {
    const numbers = rows.filter((r) => r.number.trim());
    if (numbers.length === 0) return;
    await api.createAnalogGroup(title, numbers);
    setOpen(false);
    setTitle("");
    setRows([{ number: "", brand: "", is_original: true }]);
    toast.show(t("profile.saved"));
    load();
  };

  const delRef = async (id: number) => {
    await api.deleteAnalogRef(id);
    load();
  };

  return (
    <div>
      <PageHeader
        title={t("admin.analogs")}
        action={<button className="fab" onClick={() => setOpen(true)}><Icon name="plus" size={20} strokeWidth={2.2} /></button>}
      />

      <form className="searchbar" onSubmit={(e) => { e.preventDefault(); load(); }}>
        <Icon name="search" size={19} className="ic" />
        <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t("admin.originalNumber")} />
      </form>

      {loading ? (
        <SkeletonCards count={3} height={120} />
      ) : (
        <div className="stack">
          {groups.map((g) => (
            <div className="card card-pad" key={g.id}>
              <div className="bold mb row" style={{ gap: 8 }}><Icon name="link" size={16} /> {g.title || `#${g.id}`}</div>
              {g.references.map((r) => (
                <div className="between" key={r.id} style={{ padding: "5px 0" }}>
                  <span className="small row" style={{ gap: 6 }}>
                    {r.is_original && <span className="badge badge-green">{t("admin.isOriginal")}</span>}
                    <span className="tnum">{r.number_raw || r.number}</span> <span className="muted">{r.brand}</span>
                  </span>
                  <button className="btn btn-sm btn-danger" onClick={() => delRef(r.id)}><Icon name="x" size={14} /></button>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}

      <Sheet open={open} onClose={() => setOpen(false)} title={t("admin.addAnalogGroup")}>
        <div className="field"><label>{t("checkout.name")}</label><input className="input" value={title} onChange={(e) => setTitle(e.target.value)} /></div>
        {rows.map((r, i) => (
          <div className="row mb" key={i} style={{ gap: 6 }}>
            <input className="input tnum" style={{ flex: 2 }} placeholder={t("product.oem")} value={r.number} onChange={(e) => setRows((rs) => rs.map((x, j) => (j === i ? { ...x, number: e.target.value } : x)))} />
            <input className="input" style={{ flex: 1 }} placeholder={t("product.partBrand")} value={r.brand} onChange={(e) => setRows((rs) => rs.map((x, j) => (j === i ? { ...x, brand: e.target.value } : x)))} />
            <label className="small" style={{ display: "flex", alignItems: "center", gap: 4, flex: "none" }}>
              <input type="checkbox" checked={r.is_original} onChange={(e) => setRows((rs) => rs.map((x, j) => (j === i ? { ...x, is_original: e.target.checked } : x)))} /> O
            </label>
          </div>
        ))}
        <button className="btn btn-secondary btn-sm mb" onClick={() => setRows((rs) => [...rs, { number: "", brand: "", is_original: false }])}>
          <Icon name="plus" size={14} /> {t("admin.analogNumber")}
        </button>
        <button className="btn btn-block" onClick={createGroup}>{t("common.add")}</button>
      </Sheet>
    </div>
  );
}
