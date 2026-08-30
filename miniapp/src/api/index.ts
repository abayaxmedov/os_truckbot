import { request } from "./client";
import type {
  AdminPayout,
  AdminSeller,
  AdminStats,
  AnalogGroup,
  AuthResponse,
  Banner,
  BonusTxn,
  Cart,
  Category,
  Master,
  Order,
  OrderListItem,
  Page,
  Payout,
  Product,
  ProductListItem,
  Review,
  SellerOrderRow,
  SellerStats,
  TruckBrand,
  User,
} from "./types";

export * from "./types";

// ---- Auth / profile ----
export const authTelegram = (init_data: string, dev_telegram_id?: number) =>
  request<AuthResponse>("/auth/telegram", { body: { init_data, dev_telegram_id } });
export const getMe = () => request<User>("/me");
export const updateMe = (data: Partial<Pick<User, "first_name" | "last_name" | "phone" | "language">>) =>
  request<User>("/me", { method: "PATCH", body: data });
export const onboard = (role: "buyer" | "master") => request<User>("/me/onboard", { body: { role } });

// ---- Master (usta) ----
export interface MasterRegisterData {
  first_name: string;
  last_name?: string;
  phone?: string;
  photo?: string;
  address?: string;
  card_number?: string;
}
export const masterRegister = (data: MasterRegisterData) => request<Master>("/master/register", { body: data });
export const getMaster = () => request<Master>("/master");
export const getMasterTransactions = () => request<BonusTxn[]>("/master/transactions");
export const getMasterPayouts = () => request<Payout[]>("/master/payouts");

// ---- Catalog ----
export const getBrands = () => request<TruckBrand[]>("/brands");
export const getCategories = () => request<Category[]>("/categories");
export const getBanners = () => request<Banner[]>("/banners");
export const getPopular = (limit = 10) => request<ProductListItem[]>("/popular", { query: { limit } });

// ---- Products / search ----
export interface ProductQuery {
  q?: string;
  category_id?: number;
  brand_id?: number;
  model_id?: number;
  engine?: string;
  seller_id?: number;
  min_price?: number;
  max_price?: number;
  sort?: string;
  page?: number;
  page_size?: number;
}
export const listProducts = (q: ProductQuery = {}) =>
  request<Page<ProductListItem>>("/products", { query: q as Record<string, string | number | undefined> });
export const getProduct = (id: number) => request<Product>(`/products/${id}`);
export const getProductAnalogs = (id: number) => request<ProductListItem[]>(`/products/${id}/analogs`);

// ---- Cart ----
export const getCart = () => request<Cart>("/cart");
export const addToCart = (product_id: number, quantity = 1) =>
  request<Cart>("/cart/items", { body: { product_id, quantity } });
export const updateCartItem = (id: number, quantity: number) =>
  request<Cart>(`/cart/items/${id}`, { method: "PATCH", body: { quantity } });
export const removeCartItem = (id: number) => request<Cart>(`/cart/items/${id}`, { method: "DELETE" });
export const clearCart = () => request<{ detail: string }>("/cart", { method: "DELETE" });

// ---- Orders ----
export interface CheckoutData {
  contact_name: string;
  phone: string;
  city?: string;
  address?: string;
  comment?: string;
  latitude?: number | null;
  longitude?: number | null;
  payment_method?: string;
}
export const checkout = (data: CheckoutData) => request<Order>("/orders", { body: data });
export const listOrders = (page = 1) =>
  request<Page<OrderListItem>>("/orders", { query: { page } });
export const getOrder = (id: number) => request<Order>(`/orders/${id}`);
export const payOrder = (id: number, provider: string) =>
  request<{ payment_url: string; provider: string; status: string }>(`/orders/${id}/pay`, {
    body: { provider },
  });

// ---- Reviews / messages ----
export const createReview = (seller_order_id: number, stars: number, comment = "") =>
  request<Review>("/reviews", { body: { seller_order_id, stars, comment } });
export const sellerReviews = (seller_id: number) => request<Review[]>(`/reviews/seller/${seller_id}`);
export const sendMessage = (data: { product_id?: number; order_id?: number; to_user_id?: number; text: string; kind?: string }) =>
  request("/messages", { body: data });

// ---- Favorites ----
export const getFavProducts = () => request<ProductListItem[]>("/favorites/products");
export const addFavProduct = (product_id: number) => request("/favorites/products", { body: { product_id } });
export const removeFavProduct = (product_id: number) =>
  request(`/favorites/products/${product_id}`, { method: "DELETE" });
export const getFavSellers = () => request("/favorites/sellers");
export const addFavSeller = (seller_id: number) => request("/favorites/sellers", { body: { seller_id } });
export const removeFavSeller = (seller_id: number) =>
  request(`/favorites/sellers/${seller_id}`, { method: "DELETE" });

// ---- Seller cabinet ----
export const sellerRegister = (shop_name: string, description = "") =>
  request("/seller/register", { body: { shop_name, description } });
export const getSellerProfile = () => request("/seller");
export const getSellerStats = () => request<SellerStats>("/seller/stats");
export const getSellerProducts = (page = 1) =>
  request<Page<ProductListItem>>("/seller/products", { query: { page } });
export const createSellerProduct = (data: unknown) => request<Product>("/seller/products", { body: data });
export const updateSellerProduct = (id: number, data: unknown) =>
  request<Product>(`/seller/products/${id}`, { method: "PATCH", body: data });
export const deleteSellerProduct = (id: number) =>
  request(`/seller/products/${id}`, { method: "DELETE" });
export const uploadProductImage = (id: number, file: File) => {
  const form = new FormData();
  form.append("file", file);
  return request<Product>(`/seller/products/${id}/images`, { form });
};
export const importProducts = (file: File) => {
  const form = new FormData();
  form.append("file", file);
  return request<{ created: number; errors: { row: number; error: string }[] }>("/seller/products/import", { form });
};
export const getSellerOrders = (status?: string) =>
  request<SellerOrderRow[]>("/seller/orders", { query: { status } });
export const updateSellerOrderStatus = (id: number, status: string) =>
  request(`/seller/orders/${id}/status`, { method: "PATCH", query: { status } });

// ---- Admin ----
export const getAdminStats = () => request<AdminStats>("/admin/stats");
export const getAdminSellers = () => request<AdminSeller[]>("/admin/sellers");
export const setSellerStatus = (id: number, status: string) =>
  request(`/admin/sellers/${id}/status`, { method: "PATCH", body: { status } });
export const setSellerCommission = (id: number, commission_override: number | null) =>
  request(`/admin/sellers/${id}/commission`, { method: "PATCH", body: { commission_override } });
export const deleteSeller = (id: number) => request(`/admin/sellers/${id}`, { method: "DELETE" });
export const adminProducts = (status?: string, q?: string, page = 1) =>
  request<Page<ProductListItem>>("/admin/products", { query: { status, q, page } });
export const moderateProduct = (id: number, status: string) =>
  request(`/admin/products/${id}/moderate`, { method: "PATCH", body: { status } });
export const adminDeleteProduct = (id: number) => request(`/admin/products/${id}`, { method: "DELETE" });
export const createCategory = (data: unknown) => request("/admin/categories", { body: data });
export const updateCategory = (id: number, data: unknown) =>
  request(`/admin/categories/${id}`, { method: "PATCH", body: data });
export const deleteCategory = (id: number) => request(`/admin/categories/${id}`, { method: "DELETE" });
export const getAdminSettings = () => request<Record<string, string>>("/admin/settings");
export const setCommission = (default_percent: number) =>
  request("/admin/settings/commission", { method: "PATCH", body: { default_percent } });
export const getAdminBanners = () => request<Banner[]>("/admin/banners");
export const createBanner = (data: unknown) => request<Banner>("/admin/banners", { body: data });
export const updateBanner = (id: number, data: unknown) =>
  request<Banner>(`/admin/banners/${id}`, { method: "PATCH", body: data });
export const deleteBanner = (id: number) => request(`/admin/banners/${id}`, { method: "DELETE" });
export const listAnalogs = (number?: string) =>
  request<AnalogGroup[]>("/admin/analogs", { query: { number } });
export const createAnalogGroup = (title: string, numbers: { number: string; brand: string; is_original: boolean }[]) =>
  request<AnalogGroup>("/admin/analogs", { body: { title, numbers } });
export const addAnalogNumber = (groupId: number, data: { number: string; brand: string; is_original: boolean }) =>
  request<AnalogGroup>(`/admin/analogs/${groupId}/numbers`, { body: data });
export const deleteAnalogRef = (id: number) =>
  request(`/admin/analogs/references/${id}`, { method: "DELETE" });
export const setProductBonus = (id: number, bonus: number) =>
  request(`/admin/products/${id}/bonus`, { method: "PATCH", body: { bonus } });
export const getAdminPayouts = (status?: string) =>
  request<AdminPayout[]>("/admin/payouts", { query: { status } });
export const updatePayout = (id: number, action: "paid" | "rejected") =>
  request(`/admin/payouts/${id}`, { method: "PATCH", query: { action } });
export const runPayouts = () => request<{ detail: string }>("/admin/payouts/run", { method: "POST" });

// ---- Uploads ----
export const uploadImage = (file: File, subdir = "misc") => {
  const form = new FormData();
  form.append("file", file);
  return request<{ path: string; url: string }>("/uploads/image", { form, query: { subdir } });
};
