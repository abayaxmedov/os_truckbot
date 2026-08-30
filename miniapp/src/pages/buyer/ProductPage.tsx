import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import * as api from "@/api";
import { mediaUrl } from "@/api/client";
import { CartControl } from "@/components/CartControl";
import { Icon } from "@/components/Icon";
import { Placeholder } from "@/components/Placeholder";
import { ProductCard } from "@/components/ProductCard";
import { Sheet } from "@/components/Sheet";
import { Loader, Stars, useToast } from "@/components/ui";
import { useApi } from "@/lib/useApi";
import { formatMoney } from "@/lib/format";
import { useAuth } from "@/store/auth";
import { useCart } from "@/store/cart";
import { haptic } from "@/telegram/telegram";

export function ProductPage() {
  const { id } = useParams();
  const pid = Number(id);
  const { t } = useTranslation();
  const nav = useNavigate();
  const toast = useToast();
  const cart = useCart();

  const [activeImg, setActiveImg] = useState(0);
  const [askOpen, setAskOpen] = useState(false);
  const [question, setQuestion] = useState("");

  const isMaster = useAuth((s) => s.user?.is_master);
  const { data: p, loading } = useApi(() => api.getProduct(pid), [pid]);
  const { data: analogs } = useApi(() => api.getProductAnalogs(pid), [pid]);

  if (loading || !p) return <Loader />;

  const buyNow = async () => {
    if (cart.qtyOf(p.id) === 0) await cart.add(p.id);
    haptic("success");
    nav("/cart");
  };

  const sendQuestion = async () => {
    if (!question.trim()) return;
    await api.sendMessage({ product_id: p.id, text: question.trim(), kind: "question" });
    setAskOpen(false);
    setQuestion("");
    toast.show(t("product.questionSent"));
  };

  const spec = (icon: string, label: string, value?: string) =>
    value ? (
      <div className="between" style={{ padding: "11px 0", borderBottom: "1px solid var(--border)" }}>
        <span className="row muted small" style={{ gap: 8 }}>
          <Icon name={icon} size={16} /> {label}
        </span>
        <span className="small" style={{ textAlign: "right", maxWidth: "58%", fontWeight: 600 }}>{value}</span>
      </div>
    ) : null;

  const img = p.images[activeImg]?.url ? mediaUrl(p.images[activeImg].url) : "";

  return (
    <div>
      <div className="card mb">
        {img ? (
          <img src={img} alt={p.name} style={{ width: "100%", aspectRatio: "1/1", objectFit: "cover", display: "block" }} />
        ) : (
          <Placeholder size={64} />
        )}
      </div>
      {p.images.length > 1 && (
        <div className="chips mb">
          {p.images.map((im, i) => (
            <img
              key={im.id}
              src={mediaUrl(im.url)}
              onClick={() => setActiveImg(i)}
              style={{ width: 54, height: 54, borderRadius: 10, objectFit: "cover", border: i === activeImg ? "2px solid var(--brand)" : "1px solid var(--border)", cursor: "pointer" }}
            />
          ))}
        </div>
      )}

      <div className="between" style={{ alignItems: "flex-start", marginBottom: 10 }}>
        <h1 className="page-title" style={{ margin: 0, fontSize: 21 }}>{p.name}</h1>
        <span className={`badge ${p.in_stock ? "badge-green" : "badge-red"}`} style={{ flex: "none", marginTop: 4 }}>
          {p.in_stock ? t("product.inStock") : t("product.outOfStock")}
        </span>
      </div>
      <div className="bold tnum mb" style={{ fontSize: 26, letterSpacing: "-0.02em" }}>
        {formatMoney(p.price)} <span className="small muted" style={{ fontSize: 14 }}>{t("common.sum")}</span>
      </div>
      {isMaster && p.bonus > 0 && (
        <div className="card card-pad mb row" style={{ gap: 10, background: "var(--success-tint)", border: 0 }}>
          <Icon name="gift" size={20} style={{ color: "var(--success)" }} />
          <span className="small" style={{ fontWeight: 600, color: "var(--success)" }}>
            {t("product.bonus")}: +{formatMoney(p.bonus)} {t("common.sum")}
          </span>
        </div>
      )}

      <div className="card card-pad" style={{ paddingTop: 4, paddingBottom: 4 }}>
        {spec("tag", t("product.article"), p.article)}
        {spec("wrench", t("product.oem"), p.oem_number)}
        {spec("sparkles", t("product.partBrand"), p.part_brand)}
        {spec("settings", t("catalog.engine"), p.engine)}
        {spec("shield", t("product.warranty"), p.warranty)}
        {spec("truck", t("product.compatible"), p.vehicles.map((v) => v.brand_name + (v.model_name ? ` ${v.model_name}` : "")).join(", "))}
      </div>

      {p.seller && (
        <div className="list mt" onClick={() => nav(`/catalog?seller_id=${p.seller!.id}`)}>
          <div className="list-row">
            <span className="icon-chip" style={{ width: 38, height: 38 }}><Icon name="store" size={19} /></span>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 600 }}>{p.seller.shop_name}</div>
              <div className="small muted row" style={{ gap: 5 }}>
                <Stars value={p.seller.rating} size={12} /> {p.seller.rating.toFixed(1)} · {p.seller.reviews_count} {t("product.reviews")}
              </div>
            </div>
            <Icon name="chevron" size={18} className="chevron" />
          </div>
        </div>
      )}

      {p.description && (
        <>
          <div className="section-title">{t("product.description")}</div>
          <div className="card card-pad" style={{ lineHeight: 1.55 }}>{p.description}</div>
        </>
      )}

      {analogs && analogs.length > 0 && (
        <>
          <div className="section-head">
            <span className="sh-title">{t("product.analogs")}</span>
          </div>
          <div className="hscroll">
            {analogs.map((a) => (
              <ProductCard key={a.id} p={a} />
            ))}
          </div>
        </>
      )}

      <div className="action-bar">
        <div className="row" style={{ gap: 10 }}>
          <CartControl productId={p.id} inStock={p.in_stock} stockQty={p.stock_qty} variant="page" />
          <button className="btn btn-outline btn-block" disabled={!p.in_stock} onClick={buyNow}>
            {t("product.buyNow")}
          </button>
        </div>
        <button className="btn btn-secondary btn-block" onClick={() => setAskOpen(true)}>
          <Icon name="message" size={18} /> {t("product.ask")}
        </button>
      </div>

      <Sheet open={askOpen} onClose={() => setAskOpen(false)} title={t("product.ask")}>
        <textarea
          className="textarea"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder={t("product.askPlaceholder")}
          autoFocus
        />
        <button className="btn btn-block mt" onClick={sendQuestion}>
          {t("common.send")}
        </button>
      </Sheet>
    </div>
  );
}
