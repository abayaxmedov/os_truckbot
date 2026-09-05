import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import { mediaUrl } from "@/api/client";
import { ChipMultiSelect } from "@/components/ChipMultiSelect";
import { Icon } from "@/components/Icon";
import { useToast } from "@/components/ui";
import { SPECIALIZATIONS, TRUCKS } from "@/lib/masterOptions";
import { useAuth } from "@/store/auth";

export function MasterRegisterForm({ onDone }: { onDone?: () => void }) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const toast = useToast();
  const user = useAuth((s) => s.user);
  const setUser = useAuth((s) => s.setUser);
  const fileRef = useRef<HTMLInputElement>(null);

  const [form, setForm] = useState({
    first_name: user?.first_name || "",
    last_name: user?.last_name || "",
    phone: user?.phone || "",
    address: "",
    card_number: "",
    regions: "",
    work_hours: "",
    experience_years: "",
    bio: "",
    price_call: "",
    price_diagnostics: "",
    price_repair_note: "",
  });
  const [photo, setPhoto] = useState("");
  const [trucks, setTrucks] = useState<string[]>([]);
  const [specs, setSpecs] = useState<string[]>([]);
  const [is247, setIs247] = useState(false);
  const [busy, setBusy] = useState(false);
  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  // Prefill from the existing profile so this doubles as an "edit profile" form.
  useEffect(() => {
    if (!user?.is_master) return;
    api.getMaster().then((m) => {
      setForm((f) => ({
        ...f,
        address: m.address || f.address,
        card_number: m.card_number || f.card_number,
        regions: m.regions || "",
        work_hours: m.work_hours || "",
        experience_years: m.experience_years != null ? String(m.experience_years) : "",
        bio: m.bio || "",
        price_call: m.price_call != null ? String(m.price_call) : "",
        price_diagnostics: m.price_diagnostics != null ? String(m.price_diagnostics) : "",
        price_repair_note: m.price_repair_note || "",
      }));
      setTrucks(m.trucks || []);
      setSpecs(m.specializations || []);
      setIs247(!!m.is_24_7);
      if (m.photo) setPhoto(m.photo.replace(/^.*\/media\//, "").replace(/^\//, ""));
    }).catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onPhoto = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const up = await api.uploadImage(file, "misc");
    setPhoto(up.path);
  };

  const num = (v: string): number | null => {
    const n = Number(v);
    return v.trim() !== "" && !Number.isNaN(n) ? n : null;
  };

  const submit = async () => {
    if (!form.first_name.trim() || !form.phone.trim()) {
      toast.show(t("checkout.required"));
      return;
    }
    setBusy(true);
    try {
      await api.masterRegister({
        first_name: form.first_name,
        last_name: form.last_name,
        phone: form.phone,
        address: form.address,
        card_number: form.card_number,
        photo,
        trucks,
        specializations: specs,
        regions: form.regions,
        work_hours: form.work_hours,
        is_24_7: is247,
        experience_years: num(form.experience_years),
        bio: form.bio,
        price_call: num(form.price_call),
        price_diagnostics: num(form.price_diagnostics),
        price_repair_note: form.price_repair_note,
      });
      const me = await api.getMe();
      setUser(me);
      toast.show(t("profile.saved"));
      onDone?.();
    } catch (e) {
      toast.show(e instanceof Error ? e.message : t("common.error"));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <div className="center mb">
        <button
          type="button"
          onClick={() => fileRef.current?.click()}
          style={{ width: 96, height: 96, borderRadius: "50%", border: "2px dashed var(--brand)", background: "var(--surface)", color: "var(--brand)", display: "inline-flex", alignItems: "center", justifyContent: "center", overflow: "hidden", cursor: "pointer" }}
        >
          {photo ? (
            <img src={mediaUrl(photo)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          ) : (
            <Icon name="camera" size={30} strokeWidth={1.5} />
          )}
        </button>
        <div className="caption mt-sm">{t("master.photo")}</div>
        <input ref={fileRef} type="file" accept="image/*" style={{ display: "none" }} onChange={onPhoto} />
      </div>

      {/* Basics */}
      <div className="card card-pad mb">
        <div className="row" style={{ gap: 10 }}>
          <div className="field" style={{ flex: 1 }}><label>{t("master.firstName")} *</label><input className="input" value={form.first_name} onChange={(e) => set("first_name", e.target.value)} /></div>
          <div className="field" style={{ flex: 1 }}><label>{t("master.lastName")}</label><input className="input" value={form.last_name} onChange={(e) => set("last_name", e.target.value)} /></div>
        </div>
        <div className="field"><label>{t("master.phone")} *</label><input className="input" type="tel" value={form.phone} onChange={(e) => set("phone", e.target.value)} placeholder="+998" /></div>
        <div className="field"><label>{t("master.regions")}</label><input className="input" value={form.regions} onChange={(e) => set("regions", e.target.value)} placeholder={t("master.regionsHint")} /></div>
        <div className="row" style={{ gap: 10, marginBottom: 0 }}>
          <div className="field" style={{ flex: 1, marginBottom: 0 }}><label>{t("master.workHours")}</label><input className="input" value={form.work_hours} onChange={(e) => set("work_hours", e.target.value)} placeholder="9:00–20:00" /></div>
          <div className="field" style={{ flex: 1, marginBottom: 0 }}><label>{t("master.experience")}</label><input className="input tnum" inputMode="numeric" value={form.experience_years} onChange={(e) => set("experience_years", e.target.value)} placeholder="5" /></div>
        </div>
        <button type="button" className={`chip mt ${is247 ? "active" : ""}`} onClick={() => setIs247((v) => !v)}>
          {is247 ? "✓ " : ""}🚨 {t("master.is247")}
        </button>
      </div>

      {/* Trucks */}
      <div className="section-title">{t("master.trucks")}</div>
      <div className="card card-pad mb">
        <ChipMultiSelect
          options={TRUCKS.map((o) => ({ code: o.code, label: lang === "uz" ? o.uz : o.ru }))}
          value={trucks}
          onChange={setTrucks}
        />
      </div>

      {/* Specializations */}
      <div className="section-title">{t("master.specializations")}</div>
      <div className="card card-pad mb">
        <ChipMultiSelect
          options={SPECIALIZATIONS.map((o) => ({ code: o.code, label: lang === "uz" ? o.uz : o.ru }))}
          value={specs}
          onChange={setSpecs}
        />
      </div>

      {/* Prices */}
      <div className="section-title">{t("master.prices")}</div>
      <div className="card card-pad mb">
        <div className="row" style={{ gap: 10 }}>
          <div className="field" style={{ flex: 1 }}><label>{t("master.priceCall")}</label><input className="input tnum" inputMode="numeric" value={form.price_call} onChange={(e) => set("price_call", e.target.value)} placeholder="500000" /></div>
          <div className="field" style={{ flex: 1 }}><label>{t("master.priceDiagnostics")}</label><input className="input tnum" inputMode="numeric" value={form.price_diagnostics} onChange={(e) => set("price_diagnostics", e.target.value)} placeholder="150000" /></div>
        </div>
        <div className="field" style={{ marginBottom: 0 }}><label>{t("master.priceRepair")}</label><input className="input" value={form.price_repair_note} onChange={(e) => set("price_repair_note", e.target.value)} placeholder={t("master.priceRepairHint")} /></div>
      </div>

      {/* Extra */}
      <div className="card card-pad mb">
        <div className="field"><label>{t("master.bio")}</label><textarea className="textarea" value={form.bio} onChange={(e) => set("bio", e.target.value)} placeholder={t("master.bioHint")} /></div>
        <div className="field"><label>{t("master.address")}</label><input className="input" value={form.address} onChange={(e) => set("address", e.target.value)} /></div>
        <div className="field" style={{ marginBottom: 0 }}><label>{t("master.card")}</label><input className="input tnum" inputMode="numeric" value={form.card_number} onChange={(e) => set("card_number", e.target.value)} placeholder="8600 …" /></div>
      </div>

      <button className="btn btn-lg btn-block" disabled={busy} onClick={submit}>
        {busy ? <span className="spin" /> : <Icon name="check" size={18} />} {t("master.registerBtn")}
      </button>
    </div>
  );
}
