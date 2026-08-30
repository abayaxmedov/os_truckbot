import { useState } from "react";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import { Icon } from "@/components/Icon";
import { Logo } from "@/components/Logo";
import { MasterRegisterForm } from "@/components/MasterRegisterForm";
import { useAuth } from "@/store/auth";

export function OnboardingScreen() {
  const { t } = useTranslation();
  const setUser = useAuth((s) => s.setUser);
  const [step, setStep] = useState<"choose" | "master">("choose");
  const [busy, setBusy] = useState(false);

  const chooseBuyer = async () => {
    setBusy(true);
    try {
      setUser(await api.onboard("buyer"));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="app">
      <div className="page page-plain">
        {step === "choose" ? (
          <>
            <div className="center" style={{ padding: "40px 0 26px" }}>
              <Logo height={72} />
              <div className="page-title mt" style={{ marginBottom: 4 }}>{t("onboarding.title")}</div>
              <div className="muted">{t("onboarding.subtitle")}</div>
            </div>

            <button className="card card-pad btn-block mb" disabled={busy} onClick={chooseBuyer}
              style={{ background: "var(--surface)", color: "var(--text)", boxShadow: "var(--shadow-sm)", border: "1px solid var(--border)", display: "flex", alignItems: "center", gap: 14, textAlign: "left" }}>
              <span className="icon-chip" style={{ width: 46, height: 46 }}><Icon name="user" size={22} /></span>
              <span style={{ flex: 1 }}>
                <div style={{ fontWeight: 700, fontSize: 16 }}>{t("onboarding.buyer")}</div>
                <div className="caption">{t("onboarding.buyerDesc")}</div>
              </span>
              <Icon name="chevron" size={18} className="chevron" style={{ color: "var(--muted)" }} />
            </button>

            <button className="card card-pad btn-block" onClick={() => setStep("master")}
              style={{ background: "linear-gradient(120deg,var(--brand-700),var(--brand-500))", color: "#fff", border: 0, display: "flex", alignItems: "center", gap: 14, textAlign: "left" }}>
              <span style={{ width: 46, height: 46, borderRadius: 12, background: "rgba(255,255,255,0.2)", display: "inline-flex", alignItems: "center", justifyContent: "center" }}><Icon name="wrench" size={22} /></span>
              <span style={{ flex: 1 }}>
                <div style={{ fontWeight: 700, fontSize: 16 }}>{t("onboarding.master")}</div>
                <div style={{ opacity: 0.85, fontSize: 12 }}>{t("onboarding.masterDesc")}</div>
              </span>
              <Icon name="chevron" size={18} style={{ opacity: 0.8 }} />
            </button>
          </>
        ) : (
          <>
            <div className="row mb" style={{ gap: 10, marginTop: 6 }}>
              <button className="fab" style={{ background: "var(--surface-2)", color: "var(--text)", boxShadow: "none", border: "1px solid var(--border)" }} onClick={() => setStep("choose")}>
                <Icon name="arrowLeft" size={18} />
              </button>
              <div className="page-title" style={{ margin: 0, fontSize: 20 }}>{t("master.register")}</div>
            </div>
            <MasterRegisterForm />
          </>
        )}
      </div>
    </div>
  );
}
