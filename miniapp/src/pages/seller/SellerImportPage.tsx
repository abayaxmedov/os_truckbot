import { useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import { API_BASE, getToken } from "@/api/client";
import { Icon } from "@/components/Icon";
import { PageHeader } from "@/components/PageHeader";
import { useToast } from "@/components/ui";

export function SellerImportPage() {
  const { t } = useTranslation();
  const toast = useToast();
  const fileRef = useRef<HTMLInputElement>(null);
  const [result, setResult] = useState<{ created: number; errors: { row: number; error: string }[] } | null>(null);
  const [busy, setBusy] = useState(false);

  const downloadTemplate = async () => {
    const res = await fetch(API_BASE + "/api/v1/seller/products/import/template", {
      headers: { Authorization: `Bearer ${getToken()}`, "ngrok-skip-browser-warning": "true" },
    });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "products_template.xlsx";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const onFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    try {
      const res = await api.importProducts(file);
      setResult(res);
      toast.show(t("seller.imported", { count: res.created }));
    } catch (err) {
      toast.show(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setBusy(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  return (
    <div>
      <PageHeader title={t("seller.bulkImport")} subtitle="Excel / CSV" />

      <button className="card card-pad btn-block" style={{ background: "var(--surface)", color: "var(--text)", boxShadow: "var(--shadow-sm)", border: "1px solid var(--border)", display: "flex", alignItems: "center", justifyContent: "flex-start", gap: 12 }} onClick={downloadTemplate}>
        <span className="icon-chip" style={{ width: 38, height: 38 }}><Icon name="box" size={18} /></span>
        <span style={{ fontWeight: 600 }}>{t("seller.downloadTemplate")}</span>
        <Icon name="chevron" size={16} className="chevron" style={{ marginLeft: "auto", color: "var(--muted)" }} />
      </button>

      <input ref={fileRef} type="file" accept=".xlsx,.csv" style={{ display: "none" }} onChange={onFile} />
      <button
        className="card mt"
        style={{ width: "100%", padding: "28px 16px", display: "flex", flexDirection: "column", alignItems: "center", gap: 10, borderStyle: "dashed", borderColor: "var(--brand)", color: "var(--brand)", cursor: "pointer", background: "var(--surface)" }}
        disabled={busy}
        onClick={() => fileRef.current?.click()}
      >
        {busy ? <span className="spinner" /> : <Icon name="upload" size={30} strokeWidth={1.5} />}
        <span style={{ fontWeight: 600 }}>{t("seller.uploadFile")}</span>
      </button>

      {result && (
        <div className="card card-pad mt">
          <div className="row" style={{ gap: 8 }}>
            <span className="badge badge-green"><Icon name="check" size={12} strokeWidth={2.6} /> {t("seller.imported", { count: result.created })}</span>
            {result.errors.length > 0 && <span className="badge badge-red">{t("seller.importErrors", { count: result.errors.length })}</span>}
          </div>
          {result.errors.length > 0 && (
            <div className="mt-sm">
              {result.errors.map((er, i) => (
                <div key={i} className="caption">#{er.row}: {er.error}</div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
