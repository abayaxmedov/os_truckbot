import { Icon } from "@/components/Icon";

export function QtyStepper({
  value,
  onChange,
  min = 0,
  max = 9999,
}: {
  value: number;
  onChange: (v: number) => void;
  min?: number;
  max?: number;
}) {
  const btn = (dir: -1 | 1, disabled: boolean) => (
    <button
      className="fab"
      style={{ width: 32, height: 32, background: "var(--surface-2)", color: "var(--text)", boxShadow: "none", border: "1px solid var(--border)", opacity: disabled ? 0.4 : 1 }}
      disabled={disabled}
      onClick={() => onChange(value + dir)}
    >
      <Icon name={dir === 1 ? "plus" : "minus"} size={16} strokeWidth={2.2} />
    </button>
  );
  return (
    <div className="row" style={{ gap: 10 }}>
      {btn(-1, value <= min)}
      <span className="tnum" style={{ minWidth: 24, textAlign: "center", fontWeight: 700 }}>{value}</span>
      {btn(1, value >= max)}
    </div>
  );
}
