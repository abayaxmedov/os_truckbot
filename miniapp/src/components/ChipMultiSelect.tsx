import { haptic } from "@/telegram/telegram";

/** Wrapping set of toggleable chips for multi-select (trucks, specializations…). */
export function ChipMultiSelect({
  options,
  value,
  onChange,
}: {
  options: { code: string; label: string }[];
  value: string[];
  onChange: (v: string[]) => void;
}) {
  const toggle = (code: string) => {
    haptic("light");
    onChange(value.includes(code) ? value.filter((c) => c !== code) : [...value, code]);
  };
  return (
    <div className="chip-wrap">
      {options.map((o) => (
        <button
          key={o.code}
          type="button"
          className={`chip ${value.includes(o.code) ? "active" : ""}`}
          onClick={() => toggle(o.code)}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}
