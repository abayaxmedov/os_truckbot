import { useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import { mediaUrl } from "@/api/client";
import { Icon } from "@/components/Icon";
import { PageHeader } from "@/components/PageHeader";
import { SkeletonCards } from "@/components/Skeleton";
import { useToast } from "@/components/ui";
import { useApi } from "@/lib/useApi";

export function AdminBannersPage() {
  const { t } = useTranslation();
  const toast = useToast();
  const fileRef = useRef<HTMLInputElement>(null);
  const { data, loading, reload } = useApi(() => api.getAdminBanners(), []);
  const [title, setTitle] = useState("");
  const [target, setTarget] = useState("");
  const [busy, setBusy] = useState(false);

  const onFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    try {
      const up = await api.uploadImage(file, "banners");
      await api.createBanner({ title, target, image: up.path, is_active: true });
      setTitle("");
      setTarget("");
      toast.show(t("profile.saved"));
      reload();
    } finally {
      setBusy(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  return (
    <div>
      <PageHeader title={t("admin.banners")} />

      <div className="card card-pad mb">
        <div className="field"><label>{t("checkout.name")}</label><input className="input" value={title} onChange={(e) => setTitle(e.target.value)} /></div>
        <div className="field" style={{ marginBottom: 14 }}><label>Target (URL / /product/1)</label><input className="input" value={target} onChange={(e) => setTarget(e.target.value)} /></div>
        <input ref={fileRef} type="file" accept="image/*" style={{ display: "none" }} onChange={onFile} />
        <button className="btn btn-block" disabled={busy} onClick={() => fileRef.current?.click()}>
          {busy ? <span className="spin" /> : <Icon name="image" size={18} />} {t("admin.addBanner")}
        </button>
      </div>

      {loading ? (
        <SkeletonCards count={2} height={120} />
      ) : (
        <div className="stack">
          {(data || []).map((b) => (
            <div className="card" key={b.id} style={{ padding: 10 }}>
              <img src={mediaUrl(b.image)} style={{ width: "100%", borderRadius: 10, display: "block" }} />
              <div className="between mt-sm">
                <span className="small" style={{ fontWeight: 600 }}>{b.title || b.target || `#${b.id}`}</span>
                <div className="row" style={{ gap: 6 }}>
                  <button className="btn btn-sm btn-secondary" onClick={async () => { await api.updateBanner(b.id, { ...b, is_active: !b.is_active }); reload(); }}>
                    {b.is_active ? t("common.yes") : t("common.no")}
                  </button>
                  <button className="btn btn-sm btn-danger" onClick={async () => { await api.deleteBanner(b.id); reload(); }}><Icon name="trash" size={14} /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
