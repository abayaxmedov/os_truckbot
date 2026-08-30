import { brandColor } from "@/lib/format";

// Trademark-safe stylized brand badge (not the official copyrighted logo):
// a colored monogram square + the brand name in a refined typographic treatment.
export function BrandLogo({
  name,
  slug,
  active = false,
  onClick,
}: {
  name: string;
  slug: string;
  active?: boolean;
  onClick?: () => void;
}) {
  const color = brandColor(slug);
  return (
    <button
      className="chip"
      onClick={onClick}
      style={
        active
          ? { background: color, borderColor: color, color: "#fff", boxShadow: "var(--shadow-md)" }
          : undefined
      }
    >
      <span
        aria-hidden
        style={{
          width: 20,
          height: 20,
          borderRadius: 6,
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 11,
          fontWeight: 800,
          background: active ? "rgba(255,255,255,0.22)" : color,
          color: "#fff",
          letterSpacing: "-0.03em",
        }}
      >
        {name.slice(0, 2).toUpperCase()}
      </span>
      <span style={{ fontWeight: 700, letterSpacing: "-0.01em" }}>{name}</span>
    </button>
  );
}
