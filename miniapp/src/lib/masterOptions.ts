// Options for the master (usta) service profile — truck makes they service and
// their specializations. Stored as codes; labels localized here.

export interface Opt {
  code: string;
  ru: string;
  uz: string;
}

export const TRUCKS: Opt[] = [
  { code: "man", ru: "MAN", uz: "MAN" },
  { code: "volvo", ru: "Volvo", uz: "Volvo" },
  { code: "daf", ru: "DAF", uz: "DAF" },
  { code: "scania", ru: "Scania", uz: "Scania" },
  { code: "mercedes-benz", ru: "Mercedes-Benz", uz: "Mercedes-Benz" },
  { code: "renault-trucks", ru: "Renault", uz: "Renault" },
  { code: "iveco", ru: "Iveco", uz: "Iveco" },
  { code: "isuzu", ru: "Isuzu", uz: "Isuzu" },
  { code: "other", ru: "Другое", uz: "Boshqa" },
];

export const SPECIALIZATIONS: Opt[] = [
  { code: "dvigatel", ru: "Двигатель", uz: "Dvigatel" },
  { code: "kpp", ru: "КПП", uz: "KPP" },
  { code: "elektrik", ru: "Электрика", uz: "Elektrika" },
  { code: "ebs_abs", ru: "EBS/ABS", uz: "EBS/ABS" },
  { code: "tormoz", ru: "Тормозная система", uz: "Tormoz tizimi" },
  { code: "pnevmo", ru: "Пневмосистема", uz: "Pnevmotizim" },
  { code: "xodovaya", ru: "Ходовая", uz: "Xodovoy qism" },
  { code: "diagnostika", ru: "Диагностика", uz: "Diagnostika" },
  { code: "forsunka", ru: "Форсунки", uz: "Forsunka" },
  { code: "turbina", ru: "Турбина", uz: "Turbina" },
  { code: "sovutish", ru: "Охлаждение", uz: "Sovutish tizimi" },
  { code: "adblue", ru: "AdBlue / SCR", uz: "AdBlue / SCR" },
  { code: "ecu", ru: "ECU / компьютер", uz: "ECU / kompyuter" },
  { code: "shina", ru: "Шиномонтаж", uz: "Shina" },
  { code: "payvandlash", ru: "Сварка", uz: "Payvandlash" },
];

const label = (list: Opt[], code: string, lang: string): string => {
  const o = list.find((x) => x.code === code);
  if (!o) return code;
  return lang === "uz" ? o.uz : o.ru;
};

export const truckLabel = (code: string, lang: string) => label(TRUCKS, code, lang);
export const specLabel = (code: string, lang: string) => label(SPECIALIZATIONS, code, lang);

/** Map a list of codes to localized labels (unknown codes are dropped). */
export function labelsFor(list: Opt[], codes: string[], lang: string): string[] {
  return codes.map((c) => label(list, c, lang)).filter(Boolean);
}
