import { useState } from "react";

import { Icon } from "@/components/Icon";
import { Sheet } from "@/components/Sheet";
import { haptic } from "@/telegram/telegram";

export interface Option<T> {
  value: T | "";
  label: string;
  hint?: string;
}

/** Native-feeling picker: a field-styled trigger that opens a bottom sheet of
 *  options. Replaces raw <select>, which looks like a bare web form control. */
export function SelectSheet<T extends string | number>({
  value,
  options,
  onChange,
  title,
  placeholder = "—",
  icon,
}: {
  value: T | "";
  options: Option<T>[];
  onChange: (v: T | "") => void;
  title: string;
  placeholder?: string;
  icon?: string;
}) {
  const [open, setOpen] = useState(false);
  const current = options.find((o) => o.value === value);

  const pick = (v: T | "") => {
    onChange(v);
    haptic("light");
    setOpen(false);
  };

  return (
    <>
      <button type="button" className="select-trigger" onClick={() => setOpen(true)}>
        {icon && <Icon name={icon} size={17} className="st-icon" />}
        <span className={current ? "st-value" : "st-placeholder"}>{current ? current.label : placeholder}</span>
        <Icon name="chevronDown" size={17} className="st-chevron" />
      </button>

      <Sheet open={open} onClose={() => setOpen(false)} title={title}>
        <div className="list">
          {options.map((o) => {
            const active = o.value === value;
            return (
              <button key={String(o.value)} className="list-row" onClick={() => pick(o.value)}>
                <span style={{ flex: 1, fontWeight: active ? 700 : 500 }}>
                  {o.label}
                  {o.hint && <span className="caption" style={{ display: "block" }}>{o.hint}</span>}
                </span>
                {active && <Icon name="check" size={19} strokeWidth={2.4} style={{ color: "var(--brand)" }} />}
              </button>
            );
          })}
        </div>
      </Sheet>
    </>
  );
}
