import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import { Icon } from "@/components/Icon";
import { Segmented } from "@/components/Segmented";
import { useToast } from "@/components/ui";
import { formatMoney } from "@/lib/format";
import { setLanguage } from "@/i18n";
import { useAuth } from "@/store/auth";

export function ProfilePage() {
  const { t, i18n } = useTranslation();
  const nav = useNavigate();
  const toast = useToast();
  const user = useAuth((s) => s.user);
  const setUser = useAuth((s) => s.setUser);

  const [form, setForm] = useState({
    first_name: user?.first_name || "",
    last_name: user?.last_name || "",
    phone: user?.phone || "",
  });
  const [saving, setSaving] = useState(false);
  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const save = async () => {
    setSaving(true);
    try {
      setUser(await api.updateMe(form));
      toast.show(t("profile.saved"));
    } finally {
      setSaving(false);
    }
  };

  const switchLang = async (lang: "ru" | "uz") => {
    setLanguage(lang);
    try {
      setUser(await api.updateMe({ language: lang }));
    } catch {
      /* ignore */
    }
  };

  const initials = (user?.first_name || "U").slice(0, 1).toUpperCase();

  return (
    <div>
      <div className="row mb" style={{ gap: 14, marginTop: 6 }}>
        <div
          style={{ width: 60, height: 60, borderRadius: "50%", background: "linear-gradient(135deg,var(--brand-500),var(--brand-700))", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 24, fontWeight: 800, flex: "none" }}
        >
          {initials}
        </div>
        <div style={{ minWidth: 0 }}>
          <div className="page-title" style={{ margin: 0, fontSize: 20 }}>{[user?.first_name, user?.last_name].filter(Boolean).join(" ") || t("profile.title")}</div>
          <div className="caption">@{user?.username || user?.telegram_id}</div>
        </div>
      </div>

      <div className="card card-pad">
        <div className="field">
          <label>{t("profile.name")}</label>
          <input className="input" value={form.first_name} onChange={(e) => set("first_name", e.target.value)} />
        </div>
        <div className="field">
          <label>{t("profile.lastName")}</label>
          <input className="input" value={form.last_name} onChange={(e) => set("last_name", e.target.value)} />
        </div>
        <div className="field" style={{ marginBottom: 14 }}>
          <label>{t("profile.phone")}</label>
          <input className="input" type="tel" value={form.phone} onChange={(e) => set("phone", e.target.value)} placeholder="+998" />
        </div>
        <button className="btn btn-block" disabled={saving} onClick={save}>
          {saving ? <span className="spin" /> : null} {t("common.save")}
        </button>
      </div>

      <div className="section-title">{t("profile.language")}</div>
      <Segmented
        value={i18n.language === "uz" ? "uz" : "ru"}
        onChange={(v) => switchLang(v as "ru" | "uz")}
        options={[
          { value: "ru", label: "🇷🇺 Русский" },
          { value: "uz", label: "🇺🇿 O‘zbekcha" },
        ]}
      />

      <div className="section-title">{t("profile.favorites")}</div>
      <div className="list">
        <button className="list-row" onClick={() => nav("/favorites")}>
          <span className="icon-chip" style={{ width: 34, height: 34 }}><Icon name="heart" size={17} /></span>
          <span>{t("profile.favorites")}</span>
          <Icon name="chevron" size={18} className="chevron" />
        </button>
      </div>

      <div className="section-title">{t("master.cabinet")}</div>
      <div className="list">
        <button className="list-row" onClick={() => nav("/master")}>
          <span className="icon-chip" style={{ width: 34, height: 34 }}><Icon name="wrench" size={17} /></span>
          <span>{user?.is_master ? t("master.cabinet") : t("master.becomeMaster")}</span>
          <span className="chevron">
            {user?.is_master && user.master ? (
              <span className="badge badge-brand tnum">{formatMoney(user.master.balance)} {t("common.sum")}</span>
            ) : null}
            <Icon name="chevron" size={16} />
          </span>
        </button>
      </div>

      <div className="section-title">{t("nav.seller")} / {t("nav.admin")}</div>
      <div className="list">
        <button className="list-row" onClick={() => nav("/seller")}>
          <span className="icon-chip" style={{ width: 34, height: 34 }}><Icon name="store" size={17} /></span>
          <span>{user?.is_seller ? t("profile.sellerCabinet") : t("profile.becomeSeller")}</span>
          <Icon name="chevron" size={18} className="chevron" />
        </button>
        {user?.is_admin && (
          <button className="list-row" onClick={() => nav("/admin")}>
            <span className="icon-chip" style={{ width: 34, height: 34 }}><Icon name="shield" size={17} /></span>
            <span>{t("profile.adminPanel")}</span>
            <Icon name="chevron" size={18} className="chevron" />
          </button>
        )}
      </div>
    </div>
  );
}
