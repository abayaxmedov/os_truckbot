import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { showBackButton } from "@/telegram/telegram";

/** Shows the Telegram BackButton and navigates back (or to a fallback) when tapped. */
export function useBackButton(fallback = "/") {
  const nav = useNavigate();
  useEffect(() => {
    const cleanup = showBackButton(() => {
      if (window.history.length > 1) nav(-1);
      else nav(fallback);
    });
    return cleanup;
  }, [nav, fallback]);
}
