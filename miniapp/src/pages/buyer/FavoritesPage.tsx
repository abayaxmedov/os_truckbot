import { useTranslation } from "react-i18next";

import * as api from "@/api";
import { PageHeader } from "@/components/PageHeader";
import { ProductCard } from "@/components/ProductCard";
import { SkeletonGrid } from "@/components/Skeleton";
import { Empty } from "@/components/ui";
import { useApi } from "@/lib/useApi";

export function FavoritesPage() {
  const { t } = useTranslation();
  const products = useApi(() => api.getFavProducts(), []);

  return (
    <div>
      <PageHeader title={t("profile.favProducts")} />
      {products.loading ? (
        <SkeletonGrid count={4} />
      ) : (products.data || []).length === 0 ? (
        <Empty icon="heart" text={t("common.empty")} />
      ) : (
        <div className="grid">
          {(products.data || []).map((p) => (
            <ProductCard key={p.id} p={p} />
          ))}
        </div>
      )}
    </div>
  );
}
