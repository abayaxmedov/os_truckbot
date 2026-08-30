import { createContext, useCallback, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";

import { Icon } from "@/components/Icon";
import { statusTone } from "@/lib/format";

export function Loader() {
  return (
    <div className="loader">
      <div className="spinner" />
    </div>
  );
}

export function Empty({ icon = "box", text, hint }: { icon?: string; text: string; hint?: string }) {
  return (
    <div className="empty-state">
      <div className="es-ic">
        <Icon name={icon} size={32} strokeWidth={1.5} />
      </div>
      <div>
        <div className="es-title">{text}</div>
        {hint && <div className="small muted mt-sm">{hint}</div>}
      </div>
    </div>
  );
}

export function Stars({ value, size = 14 }: { value: number; size?: number }) {
  const full = Math.round(value);
  return (
    <span className="stars" style={{ gap: 1 }}>
      {[1, 2, 3, 4, 5].map((n) => (
        <Icon
          key={n}
          name="star"
          size={size}
          fill={n <= full}
          strokeWidth={1.5}
          style={{ color: n <= full ? "var(--star)" : "var(--border-strong)" }}
        />
      ))}
    </span>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const { t } = useTranslation();
  const tone = statusTone(status);
  const label = t(`status.${status}`, { defaultValue: status });
  return <span className={`badge badge-${tone}`}>{label}</span>;
}

// ---- Toast ----
interface ToastCtx {
  show: (msg: string) => void;
}
const ToastContext = createContext<ToastCtx>({ show: () => {} });

export function ToastProvider({ children }: { children: ReactNode }) {
  const [msg, setMsg] = useState<string | null>(null);
  const show = useCallback((m: string) => setMsg(m), []);
  useEffect(() => {
    if (!msg) return;
    const timer = setTimeout(() => setMsg(null), 1900);
    return () => clearTimeout(timer);
  }, [msg]);
  return (
    <ToastContext.Provider value={{ show }}>
      {children}
      {msg && (
        <div className="toast">
          <Icon name="check" size={16} strokeWidth={2.4} />
          {msg}
        </div>
      )}
    </ToastContext.Provider>
  );
}

export function useToast() {
  return useContext(ToastContext);
}
