import { useEffect } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { Icon } from "@/components/Icon";
import { useBackButton } from "@/components/BackButton";
import { useCart } from "@/store/cart";

const TABS = [
  { to: "/", icon: "home", key: "home", end: true },
  { to: "/catalog", icon: "grid", key: "catalog", end: false },
  { to: "/cart", icon: "cart", key: "cart", end: false },
  { to: "/orders", icon: "box", key: "orders", end: false },
  { to: "/profile", icon: "user", key: "profile", end: false },
];

export function Layout() {
  const { t } = useTranslation();
  const count = useCart((s) => s.count);
  const refresh = useCart((s) => s.refresh);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <div className="app">
      <div className="page">
        <Outlet />
      </div>
      <nav className="tabbar">
        {TABS.map((tab) => (
          <NavLink key={tab.key} to={tab.to} end={tab.end}>
            {({ isActive }) => (
              <>
                <span className="tab-icon">
                  <Icon name={tab.icon} size={23} strokeWidth={isActive ? 2.2 : 1.9} fill={false} />
                  {tab.key === "cart" && count > 0 && <span className="tab-badge">{count}</span>}
                </span>
                <span>{t(`nav.${tab.key}`)}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}

/** Full-screen layout without the tab bar; shows the Telegram BackButton. */
export function PlainLayout() {
  useBackButton();
  const refresh = useCart((s) => s.refresh);
  useEffect(() => {
    refresh();
  }, [refresh]);
  return (
    <div className="app">
      <div className="page page-plain">
        <Outlet />
      </div>
    </div>
  );
}
