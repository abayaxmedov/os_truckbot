import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import ru from "./locales/ru.json";
import uz from "./locales/uz.json";

export const STORAGE_KEY = "truckbot_lang";

function initialLang(): "ru" | "uz" {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === "ru" || saved === "uz") return saved;
  } catch {
    /* ignore */
  }
  const tgLang = window.Telegram?.WebApp?.initDataUnsafe?.user?.language_code;
  return tgLang === "uz" ? "uz" : "ru";
}

i18n.use(initReactI18next).init({
  resources: { ru: { translation: ru }, uz: { translation: uz } },
  lng: initialLang(),
  fallbackLng: "ru",
  interpolation: { escapeValue: false },
});

export function setLanguage(lang: "ru" | "uz") {
  i18n.changeLanguage(lang);
  try {
    localStorage.setItem(STORAGE_KEY, lang);
  } catch {
    /* ignore */
  }
}

export default i18n;
