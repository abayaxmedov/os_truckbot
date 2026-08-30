import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import type { ProductListItem } from "@/api/types";
import { mediaUrl } from "@/api/client";
import { Icon } from "@/components/Icon";
import { PageHeader } from "@/components/PageHeader";
import { Placeholder } from "@/components/Placeholder";
import { Segmented } from "@/components/Segmented";
import { SkeletonCards } from "@/components/Skeleton";
import { Empty, useToast } from "@/components/ui";
import { formatMoney } from "@/lib/format";

export function AdminModerationPage() {
  const { t } = useTranslation();
  const nav = useNavigate();
  const toast = useToast();
  const [status, setStatus] = useState("pending");
  const [items, setItems] = useState<ProductListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [bonuses, setBonuses] = useState<Record<number, string>>({});

  const load = () => {
    setLoading(true);
    api.adminProducts(status).then((r) => {
      setItems(r.items);
      setBonuses(Object.fromEntries(r.items.map((p) => [p.id, String(p.bonus || 0)])));
    }).finally(() => setLoading(false));
  };
  useEffect(load, [status]);

  const moderate = async (id: number, s: string) => {
    await api.moderateProduct(id, s);
    toast.show(t("profile.saved"));
    load();
  };

  const saveBonus = async (id: number) => {
    await api.setProductBonus(id, Number(bonuses[id] || 0));
    toast.show(t("profile.saved"));
  };

  return (
    <div>
      <PageHeader title={t("admin.moderation")} />
      <div className="mb">
        <Segmented
          value={status}
          onChange={setStatus}
          options={["pending", "approved", "rejected"].map((f) => ({ value: f, label: t(`seller.moderation${f.charAt(0).toUpperCase() + f.slice(1)}`) }))}
        />
      </div>

      {loading ? (
        <SkeletonCards count={3} height={80} />
      ) : items.length === 0 ? (
        <Empty icon="check" text={t("common.empty")} />
      ) : (
        <div className="stack">
          {items.map((p) => (
            <div className="card card-pad" key={p.id}>
              <div className="row" onClick={() => nav(`/product/${p.id}`)} style={{ cursor: "pointer" }}>
                <span style={{ width: 48, height: 48, borderRadius: 10, overflow: "hidden", flex: "none" }}>
                  {p.image ? <img src={mediaUrl(p.image)} style={{ width: 48, height: 48, objectFit: "cover" }} /> : <Placeholder size={20} />}
                </span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div className="small" style={{ fontWeight: 600 }}>{p.name}</div>
                  <div className="caption tnum">{p.seller?.shop_name} · {formatMoney(p.price)} {t("common.sum")}</div>
                </div>
              </div>
              <div className="row mt" style={{ gap: 8 }}>
                <button className="btn btn-sm btn-block" onClick={() => moderate(p.id, "approved")}><Icon name="check" size={15} /> {t("admin.approve")}</button>
                <button className="btn btn-sm btn-danger btn-block" onClick={() => moderate(p.id, "rejected")}><Icon name="x" size={15} /> {t("admin.reject")}</button>
              </div>
              <div className="row mt" style={{ gap: 8 }}>
                <span className="row caption" style={{ gap: 5, flex: "none" }}><Icon name="gift" size={14} /> {t("admin.bonus")}</span>
                <input className="input tnum" style={{ flex: 1, padding: "8px 10px" }} type="number" inputMode="numeric"
                  value={bonuses[p.id] ?? ""} onChange={(e) => setBonuses((b) => ({ ...b, [p.id]: e.target.value }))} />
                <button className="btn btn-sm btn-secondary" onClick={() => saveBonus(p.id)}><Icon name="check" size={14} /></button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
