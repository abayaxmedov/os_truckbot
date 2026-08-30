export function formatMoney(n: number): string {
  return Math.round(n)
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

// Category slug -> Icon name (see components/Icon.tsx)
const CATEGORY_ICON: Record<string, string> = {
  filtry: "filter",
  "tormoznaya-sistema": "disc",
  podveska: "sliders",
  "rulevoe-upravlenie": "gauge",
  dvigatel: "settings",
  "toplivnaya-sistema": "fuel",
  sceplenie: "target",
  "korobka-peredach": "wrench",
  elektrika: "zap",
  pnevmatika: "wind",
  ohlazhdenie: "snowflake",
  "zapchasti-kabiny": "truck",
  amortizatory: "activity",
  "masla-zhidkosti": "droplet",
  remni: "link",
  podshipniki: "disc",
  datchiki: "activity",
  drugie: "box",
};

export function categoryIcon(slug: string): string {
  return CATEGORY_ICON[slug] || "box";
}

// Truck brand slug -> signature accent color (for stylized brand badges)
export const BRAND_COLOR: Record<string, string> = {
  man: "#e2001a",
  volvo: "#1f4e79",
  daf: "#0072ce",
  scania: "#0f1e82",
  "mercedes-benz": "#111111",
  "renault-trucks": "#d4001a",
  iveco: "#003a70",
};

export function brandColor(slug: string): string {
  return BRAND_COLOR[slug] || "#2b4fd6";
}

const STATUS_TONE: Record<string, "green" | "amber" | "red" | "gray"> = {
  new: "amber",
  confirmed: "amber",
  processing: "amber",
  shipped: "amber",
  delivered: "green",
  completed: "green",
  cancelled: "red",
  pending: "gray",
  paid: "green",
  failed: "red",
  approved: "green",
  rejected: "red",
  active: "green",
  blocked: "red",
};

export function statusTone(status: string): "green" | "amber" | "red" | "gray" {
  return STATUS_TONE[status] || "gray";
}
