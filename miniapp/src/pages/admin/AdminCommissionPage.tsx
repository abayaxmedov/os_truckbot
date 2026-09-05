import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import { Icon } from "@/components/Icon";
import { PageHeader } from "@/components/PageHeader";
import { Loader, useToast } from "@/components/ui";

export function AdminCommissionPage() {
  const { t } = useTranslation();
  const toast = useToast();
  const [value, setValue] = useState("");
  const [support, setSupport] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savingSupport, setSavingSupport] = useState(false);

  useEffect(() => {
    api.getAdminSettings().then((s) => {
      setValue(s.default_commission_percent ?? "");
      setSupport(s.support_telegram ?? "");
      setLoading(false);
    });
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      await api.setCommission(Number(value));
      toast.show(t("profile.saved"));
    } finally {
      setSaving(false);
    }
  };

  const saveSupport = async () => {
    setSavingSupport(true);
    try {
      await api.setSupportTelegram(support.trim().replace(/^@/, ""));
      toast.show(t("profile.saved"));
    } finally {
      setSavingSupport(false);
    }
  };

  if (loading) return <Loader />;

  return (
    <div>
      <PageHeader title={t("admin.commission")} />

      <div className="card card-pad">
        <div className="center" style={{ padding: "6px 0 16px" }}>
          <span className="icon-chip" style={{ width: 56, height: 56 }}><Icon name="percent" size={26} /></span>
          <div className="tnum" style={{ fontSize: 40, fontWeight: 800, letterSpacing: "-0.03em", marginTop: 10 }}>{value || 0}%</div>
        </div>
        <div className="field">
          <label>{t("admin.defaultCommission")}</label>
          <input className="input tnum" type="number" inputMode="decimal" value={value} onChange={(e) => setValue(e.target.value)} />
        </div>
        <div className="chips mb">
          {[5, 7, 10, 15].map((v) => (
            <div key={v} className={`chip ${Number(value) === v ? "active" : ""}`} onClick={() => setValue(String(v))}>{v}%</div>
          ))}
        </div>
        <button className="btn btn-block" disabled={saving} onClick={save}>
          {saving ? <span className="spin" /> : null} {t("common.save")}
        </button>
      </div>

      <div className="section-title">{t("admin.supportTelegram")}</div>
      <div className="card card-pad">
        <div className="field">
          <label>{t("admin.supportTelegramLabel")}</label>
          <div className="row" style={{ gap: 0, alignItems: "stretch" }}>
            <span className="input" style={{ flex: "none", width: 34, display: "flex", alignItems: "center", justifyContent: "center", borderRight: 0, borderTopRightRadius: 0, borderBottomRightRadius: 0, color: "var(--muted)" }}>@</span>
            <input
              className="input"
              style={{ borderTopLeftRadius: 0, borderBottomLeftRadius: 0 }}
              value={support}
              placeholder="truckcenter_admin"
              autoCapitalize="off"
              autoCorrect="off"
              onChange={(e) => setSupport(e.target.value.replace(/^@/, ""))}
            />
          </div>
          <div className="caption mt-sm">{t("admin.supportTelegramHint")}</div>
        </div>
        <button className="btn btn-block" disabled={savingSupport} onClick={saveSupport}>
          {savingSupport ? <span className="spin" /> : null} {t("common.save")}
        </button>
      </div>
    </div>
  );
}
