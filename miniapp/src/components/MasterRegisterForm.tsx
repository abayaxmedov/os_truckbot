import { useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import { mediaUrl } from "@/api/client";
import { Icon } from "@/components/Icon";
import { useToast } from "@/components/ui";
import { useAuth } from "@/store/auth";

export function MasterRegisterForm({ onDone }: { onDone?: () => void }) {
  const { t } = useTranslation();
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
  });
  const [photo, setPhoto] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const onPhoto = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const up = await api.uploadImage(file, "misc");
    setPhoto(up.path);
  };

  const submit = async () => {
    if (!form.first_name.trim() || !form.phone.trim()) {
      toast.show(t("checkout.required"));
      return;
    }
    setBusy(true);
    try {
      await api.masterRegister({ ...form, photo });
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

      <div className="card card-pad">
        <div className="row" style={{ gap: 10 }}>
          <div className="field" style={{ flex: 1 }}><label>{t("master.firstName")} *</label><input className="input" value={form.first_name} onChange={(e) => set("first_name", e.target.value)} /></div>
          <div className="field" style={{ flex: 1 }}><label>{t("master.lastName")}</label><input className="input" value={form.last_name} onChange={(e) => set("last_name", e.target.value)} /></div>
        </div>
        <div className="field"><label>{t("master.phone")} *</label><input className="input" type="tel" value={form.phone} onChange={(e) => set("phone", e.target.value)} placeholder="+998" /></div>
        <div className="field"><label>{t("master.address")}</label><input className="input" value={form.address} onChange={(e) => set("address", e.target.value)} /></div>
        <div className="field" style={{ marginBottom: 0 }}><label>{t("master.card")}</label><input className="input tnum" inputMode="numeric" value={form.card_number} onChange={(e) => set("card_number", e.target.value)} placeholder="8600 …" /></div>
      </div>

      <button className="btn btn-lg btn-block mt" disabled={busy} onClick={submit}>
        {busy ? <span className="spin" /> : <Icon name="check" size={18} />} {t("master.registerBtn")}
      </button>
    </div>
  );
}
