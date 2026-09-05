import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import type { AdminMaster } from "@/api/types";
import { mediaUrl } from "@/api/client";
import { Icon } from "@/components/Icon";
import { PageHeader } from "@/components/PageHeader";
import { Loader, useToast } from "@/components/ui";
import { labelsFor, SPECIALIZATIONS } from "@/lib/masterOptions";

export function AdminMastersPage() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const toast = useToast();
  const [items, setItems] = useState<AdminMaster[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<number | null>(null);

  const load = () => {
    setLoading(true);
    api.getAdminMasters().then(setItems).catch(() => setItems([])).finally(() => setLoading(false));
  };
  useEffect(load, []);

  const toggle = async (m: AdminMaster) => {
    setBusy(m.id);
    try {
      await api.setMasterVerified(m.id, !m.is_verified);
      setItems((list) => list.map((x) => (x.id === m.id ? { ...x, is_verified: !x.is_verified } : x)));
      toast.show(t("profile.saved"));
    } catch (e) {
      toast.show(e instanceof Error ? e.message : t("common.error"));
    } finally {
      setBusy(null);
    }
  };

  if (loading) return <Loader />;

  return (
    <div>
      <PageHeader title={t("admin.masters")} subtitle={`${items.length}`} />

      {items.length === 0 ? (
        <div className="card card-pad caption center">{t("masters.empty")}</div>
      ) : (
        <div className="stack">
          {items.map((m) => {
            const specs = labelsFor(SPECIALIZATIONS, m.specializations, lang);
            return (
              <div className="card card-pad" key={m.id}>
                <div className="row" style={{ gap: 12, alignItems: "center" }}>
                  {m.photo ? (
                    <img src={mediaUrl(m.photo)} className="master-ava" style={{ width: 46, height: 46 }} alt={m.name} />
                  ) : (
                    <span className="icon-chip" style={{ width: 46, height: 46, flex: "none" }}><Icon name="user" size={22} /></span>
                  )}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div className="row" style={{ gap: 6, flexWrap: "wrap" }}>
                      <span className="bold" style={{ fontSize: 15 }}>{m.name || "—"}</span>
                      {m.is_verified && (
                        <span className="badge badge-green" style={{ gap: 3 }}><Icon name="check" size={11} strokeWidth={3} /> {t("master.verified")}</span>
                      )}
                    </div>
                    <div className="caption">
                      {m.phone}
                      {m.experience_years ? ` · ${m.experience_years} ${t("master.years")}` : ""}
                    </div>
                  </div>
                </div>

                {specs.length > 0 && (
                  <div className="master-tags mt-sm">
                    {specs.slice(0, 5).map((l) => <span key={l} className="mtag">{l}</span>)}
                  </div>
                )}

                <button
                  className={`btn btn-block mt ${m.is_verified ? "btn-secondary" : ""}`}
                  disabled={busy === m.id}
                  onClick={() => toggle(m)}
                >
                  {busy === m.id ? <span className="spin" /> : <Icon name={m.is_verified ? "x" : "check"} size={16} />}
                  {m.is_verified ? t("admin.unverify") : t("admin.verify")}
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
