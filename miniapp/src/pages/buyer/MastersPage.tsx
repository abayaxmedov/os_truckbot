import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import type { MasterPublic } from "@/api/types";
import { MasterCard } from "@/components/MasterCard";
import { PageHeader } from "@/components/PageHeader";
import { SkeletonCards } from "@/components/Skeleton";
import { Empty } from "@/components/ui";
import { Icon } from "@/components/Icon";
import { useToast } from "@/components/ui";
import { SPECIALIZATIONS } from "@/lib/masterOptions";
import { getLocation, haptic } from "@/telegram/telegram";

export function MastersPage() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const toast = useToast();
  const [params, setParams] = useSearchParams();
  const [spec, setSpec] = useState(params.get("specialization") || "");
  const [items, setItems] = useState<MasterPublic[]>([]);
  const [loading, setLoading] = useState(true);
  const [dists, setDists] = useState<Record<number, { distance_km: number; eta_min: number }>>({});
  const [nearBusy, setNearBusy] = useState(false);

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

  const nearMe = async () => {
    setNearBusy(true);
    try {
      const c = await getLocation();
      if (!c) return toast.show(t("checkout.locationFail"));
      const res = await api.getMasterDistances(c.latitude, c.longitude);
      const map: Record<number, { distance_km: number; eta_min: number }> = {};
      res.forEach((d) => (map[d.id] = { distance_km: d.distance_km, eta_min: d.eta_min }));
      setDists(map);
      // Sort loaded masters by nearest (those with a distance first).
      setItems((list) => [...list].sort((a, b) => (map[a.id]?.distance_km ?? 1e9) - (map[b.id]?.distance_km ?? 1e9)));
    } finally {
      setNearBusy(false);
    }
  };

  const sorted = items;

  return (
    <div>
      <PageHeader
        title={t("masters.title")}
        action={
          <button className="btn btn-sm btn-secondary" onClick={nearMe} disabled={nearBusy}>
            {nearBusy ? <span className="spin" /> : <Icon name="pin" size={14} />} {t("masters.nearMe")}
          </button>
        }
      />

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
          {sorted.map((m) => <MasterCard key={m.id} m={m} dist={dists[m.id]} />)}
        </div>
      )}
    </div>
  );
}
