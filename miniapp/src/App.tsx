import { useEffect } from "react";
import { Route, Routes } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { Layout, PlainLayout } from "@/components/Layout";
import { Loader } from "@/components/ui";
import { useAuth } from "@/store/auth";

import { HomePage } from "@/pages/buyer/HomePage";
import { CatalogPage } from "@/pages/buyer/CatalogPage";
import { ProductPage } from "@/pages/buyer/ProductPage";
import { CartPage } from "@/pages/buyer/CartPage";
import { CheckoutPage } from "@/pages/buyer/CheckoutPage";
import { OrdersPage } from "@/pages/buyer/OrdersPage";
import { OrderDetailPage } from "@/pages/buyer/OrderDetailPage";
import { ProfilePage } from "@/pages/buyer/ProfilePage";
import { FavoritesPage } from "@/pages/buyer/FavoritesPage";

import { OnboardingScreen } from "@/pages/OnboardingScreen";
import { MasterCabinet } from "@/pages/master/MasterCabinet";

import { SellerDashboard } from "@/pages/seller/SellerDashboard";
import { SellerProductsPage } from "@/pages/seller/SellerProductsPage";
import { SellerProductForm } from "@/pages/seller/SellerProductForm";
import { SellerOrdersPage } from "@/pages/seller/SellerOrdersPage";
import { SellerImportPage } from "@/pages/seller/SellerImportPage";

import { AdminDashboard } from "@/pages/admin/AdminDashboard";
import { AdminSellersPage } from "@/pages/admin/AdminSellersPage";
import { AdminModerationPage } from "@/pages/admin/AdminModerationPage";
import { AdminCategoriesPage } from "@/pages/admin/AdminCategoriesPage";
import { AdminCommissionPage } from "@/pages/admin/AdminCommissionPage";
import { AdminBannersPage } from "@/pages/admin/AdminBannersPage";
import { AdminAnalogsPage } from "@/pages/admin/AdminAnalogsPage";
import { AdminPayoutsPage } from "@/pages/admin/AdminPayoutsPage";

export function App() {
  const { t } = useTranslation();
  const status = useAuth((s) => s.status);
  const login = useAuth((s) => s.login);
  const user = useAuth((s) => s.user);

  useEffect(() => {
    login();
  }, [login]);

  if (status === "idle" || status === "loading") {
    return (
      <div className="app">
        <div className="page">
          <Loader />
        </div>
      </div>
    );
  }
  if (status === "error") {
    return (
      <div className="app">
        <div className="page center" style={{ paddingTop: 80 }}>
          <div style={{ fontSize: 40 }}>🔌</div>
          <p className="muted">{t("auth.failed")}</p>
          <button className="btn" onClick={() => login()}>
            {t("common.retry")}
          </button>
        </div>
      </div>
    );
  }

  if (user && !user.onboarded) {
    return <OnboardingScreen />;
  }

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="/catalog" element={<CatalogPage />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/orders" element={<OrdersPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Route>

      <Route element={<PlainLayout />}>
        <Route path="/product/:id" element={<ProductPage />} />
        <Route path="/checkout" element={<CheckoutPage />} />
        <Route path="/orders/:id" element={<OrderDetailPage />} />
        <Route path="/favorites" element={<FavoritesPage />} />
        <Route path="/master" element={<MasterCabinet />} />

        <Route path="/seller" element={<SellerDashboard />} />
        <Route path="/seller/products" element={<SellerProductsPage />} />
        <Route path="/seller/products/new" element={<SellerProductForm />} />
        <Route path="/seller/products/:id/edit" element={<SellerProductForm />} />
        <Route path="/seller/orders" element={<SellerOrdersPage />} />
        <Route path="/seller/import" element={<SellerImportPage />} />

        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/admin/sellers" element={<AdminSellersPage />} />
        <Route path="/admin/moderation" element={<AdminModerationPage />} />
        <Route path="/admin/categories" element={<AdminCategoriesPage />} />
        <Route path="/admin/commission" element={<AdminCommissionPage />} />
        <Route path="/admin/banners" element={<AdminBannersPage />} />
        <Route path="/admin/analogs" element={<AdminAnalogsPage />} />
        <Route path="/admin/payouts" element={<AdminPayoutsPage />} />
      </Route>
    </Routes>
  );
}
