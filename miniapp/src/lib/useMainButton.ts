import { useEffect } from "react";

import { getWebApp, setMainButton } from "@/telegram/telegram";

/** True when Telegram's native MainButton is usable (i.e. we're inside Telegram). */
export function hasMainButton(): boolean {
  const wa = getWebApp();
  return !!wa && !!wa.MainButton && !!wa.initData;
}

/**
 * Drive Telegram's native MainButton for the screen's primary action.
 * No-op outside Telegram, so the in-page button stays the fallback.
 */
export function useMainButton(
  text: string,
  onClick: () => void,
  opts: { enabled?: boolean; visible?: boolean; progress?: boolean } = {},
) {
  const { enabled = true, visible = true, progress = false } = opts;
  useEffect(() => {
    if (!hasMainButton() || !visible) return;
    return setMainButton(text, onClick, { enabled, visible, progress });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [text, enabled, visible, progress, onClick]);
}
