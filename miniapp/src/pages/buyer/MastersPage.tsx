import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import type { MasterPublic } from "@/api/types";
import { MasterCard } from "@/components/MasterCard";
import { PageHeader } from "@/components/PageHeader";
import { SkeletonCards } from "@/components/Skeleton";
import { Empty } from "@/components/ui";
import { SPECIALIZATIONS } from "@/lib/masterOptions";
import { haptic } from "@/telegram/telegram";

export function MastersPage() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const [params, setParams] = useSearchParams();
  const [spec, setSpec] = useState(params.get("specialization") || "");
  const [items, setItems] = useState<MasterPublic[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.getMasters(spec ? { specialization: spec } : {})
      .then(setItems)
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, [spec]);

  const pick = (code: string) => {
    haptic("light");
    const next = spec === code ? "" : code;
    setSpec(next);
    setParams(next ? { specialization: next } : {}, { replace: true });
  };

  return (
    <div>
      <PageHeader title={t("masters.title")} subtitle={t("masters.subtitle")} />

      <div className="chips mb">
        <button className={`chip ${!spec ? "active" : ""}`} onClick={() => { haptic("light"); setSpec(""); setParams({}, { replace: true }); }}>
          {t("common.all")}
        </button>
        {SPECIALIZATIONS.map((o) => (
          <button key={o.code} className={`chip ${spec === o.code ? "active" : ""}`} onClick={() => pick(o.code)}>
            {lang === "uz" ? o.uz : o.ru}
          </button>
        ))}
      </div>

      {loading ? (
        <SkeletonCards count={4} height={128} />
      ) : items.length === 0 ? (
        <Empty icon="wrench" text={t("masters.empty")} />
      ) : (
        <div className="stack">
          {items.map((m) => <MasterCard key={m.id} m={m} />)}
        </div>
      )}
    </div>
  );
}
