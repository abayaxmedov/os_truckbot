import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { Logo } from "@/components/Logo";
import { MasterRegisterForm } from "@/components/MasterRegisterForm";

// Reached only for a not-yet-onboarded user who tapped "register as master" in the
// bot. The buyer-vs-master role choice now happens in the Telegram bot; here the
// master just completes their profile. On submit the user becomes onboarded and the
// app gate falls through to the marketplace.
export function OnboardingScreen() {
  const { t } = useTranslation();
  const nav = useNavigate();
  return (
    <div className="app">
      <div className="page page-plain">
        <div className="center" style={{ padding: "40px 0 22px" }}>
          <Logo height={72} />
          <div className="page-title mt" style={{ marginBottom: 4 }}>{t("master.register")}</div>
          <div className="muted">{t("onboarding.masterDesc")}</div>
        </div>
        <MasterRegisterForm onDone={() => nav("/", { replace: true })} />
      </div>
    </div>
  );
}
