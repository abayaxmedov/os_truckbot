// Manufacturing countries for parts. Stored on the product as a short code;
// labels are localized here and shown with a flag emoji.

export interface Country {
  code: string;
  flag: string;
  ru: string;
  uz: string;
}

export const COUNTRIES: Country[] = [
  { code: "de", flag: "🇩🇪", ru: "Германия", uz: "Germaniya" },
  { code: "tr", flag: "🇹🇷", ru: "Турция", uz: "Turkiya" },
  { code: "cn", flag: "🇨🇳", ru: "Китай", uz: "Xitoy" },
  { code: "ru", flag: "🇷🇺", ru: "Россия", uz: "Rossiya" },
  { code: "kr", flag: "🇰🇷", ru: "Корея", uz: "Koreya" },
  { code: "jp", flag: "🇯🇵", ru: "Япония", uz: "Yaponiya" },
  { code: "us", flag: "🇺🇸", ru: "США", uz: "AQSh" },
  { code: "it", flag: "🇮🇹", ru: "Италия", uz: "Italiya" },
  { code: "fr", flag: "🇫🇷", ru: "Франция", uz: "Fransiya" },
  { code: "nl", flag: "🇳🇱", ru: "Нидерланды", uz: "Niderlandiya" },
  { code: "pl", flag: "🇵🇱", ru: "Польша", uz: "Polsha" },
  { code: "es", flag: "🇪🇸", ru: "Испания", uz: "Ispaniya" },
  { code: "se", flag: "🇸🇪", ru: "Швеция", uz: "Shvetsiya" },
  { code: "in", flag: "🇮🇳", ru: "Индия", uz: "Hindiston" },
  { code: "my", flag: "🇲🇾", ru: "Малайзия", uz: "Malayziya" },
  { code: "other", flag: "🌍", ru: "Другое", uz: "Boshqa" },
];

const BY_CODE: Record<string, Country> = Object.fromEntries(COUNTRIES.map((c) => [c.code, c]));

export function findCountry(code: string | undefined | null): Country | undefined {
  if (!code) return undefined;
  return BY_CODE[code];
}

/** Localized display "🇩🇪 Германия"; falls back to the raw value for unknown codes. */
export function countryLabel(code: string | undefined | null, lang: string): string {
  const c = findCountry(code);
  if (!c) return code || "";
  return `${c.flag} ${lang === "uz" ? c.uz : c.ru}`;
}
