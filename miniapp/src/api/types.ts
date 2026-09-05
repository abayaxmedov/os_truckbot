export type Lang = "ru" | "uz";

export interface SellerBrief {
  id: number;
  shop_name: string;
  rating: number;
  reviews_count: number;
  orders_count: number;
  completion_rate: number;
}

export interface User {
  id: number;
  telegram_id: number;
  username: string;
  first_name: string;
  last_name: string;
  phone: string | null;
  language: Lang;
  is_admin: boolean;
  is_seller: boolean;
  is_master: boolean;
  onboarded: boolean;
  seller: { id: number; shop_name: string; status: string; rating: number; reviews_count: number } | null;
  master: { id: number; balance: number; pending: number; status: string } | null;
}

export interface Master {
  id: number;
  status: string;
  photo: string;
  address: string;
  card_number: string;
  balance: number;
  pending: number;
  total_earned: number;
  next_payout_at: string | null;
}

export interface BonusTxn {
  id: number;
  amount: number;
  status: string;
  order_id: number | null;
  note: string;
  created_at: string;
}

export interface Payout {
  id: number;
  amount: number;
  card_number: string;
  status: string;
  created_at: string;
}

export interface AdminPayout extends Payout {
  master_id: number;
  master_name: string;
  phone: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface TruckModel {
  id: number;
  name: string;
}
export interface TruckBrand {
  id: number;
  name: string;
  slug: string;
  logo: string;
  models: TruckModel[];
}

export interface Category {
  id: number;
  name: string;
  name_ru: string;
  name_uz: string;
  slug: string;
  parent_id: number | null;
  commission_override: number | null;
  sort_order: number;
  is_active: boolean;
  children: Category[];
}

export interface ProductImage {
  id: number;
  url: string;
  sort_order: number;
}
export interface Vehicle {
  id: number;
  brand_id: number;
  brand_name: string;
  model_id: number | null;
  model_name: string | null;
}

export interface ProductListItem {
  id: number;
  name: string;
  article: string;
  oem_number: string;
  part_brand: string;
  country: string;
  price: number;
  currency: string;
  stock_qty: number;
  in_stock: boolean;
  image: string | null;
  category_id: number;
  seller: SellerBrief | null;
  status: string;
  bonus: number;
}

export interface Product extends ProductListItem {
  name_ru: string;
  name_uz: string;
  description: string;
  description_ru: string;
  description_uz: string;
  warranty: string;
  engine: string;
  is_active: boolean;
  images: ProductImage[];
  vehicles: Vehicle[];
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface CartItem {
  id: number;
  product_id: number;
  name: string;
  article: string;
  price: number;
  quantity: number;
  line_total: number;
  image: string | null;
  stock_qty: number;
  seller_id: number;
  seller_name: string;
}
export interface Cart {
  id: number;
  items: CartItem[];
  subtotal: number;
  count: number;
}

export interface OrderItem {
  id: number;
  product_id: number | null;
  product_name: string;
  article: string;
  unit_price: number;
  quantity: number;
  line_total: number;
  image: string | null;
}
export interface SellerOrder {
  id: number;
  seller_id: number;
  seller_name: string;
  status: string;
  subtotal: number;
  commission_amount: number;
  seller_payout: number;
  items: OrderItem[];
  can_review: boolean;
  reviewed: boolean;
}
export interface Order {
  id: number;
  status_summary: string;
  contact_name: string;
  phone: string;
  city: string;
  address: string;
  comment: string;
  latitude: number | null;
  longitude: number | null;
  delivery_method: string;
  payment_method: string;
  payment_status: string;
  subtotal: number;
  discount: number;
  delivery_cost: number;
  total: number;
  created_at: string;
  seller_orders: SellerOrder[];
}
export interface OrderListItem {
  id: number;
  status_summary: string;
  total: number;
  payment_status: string;
  items_count: number;
  created_at: string;
}

export interface SellerOrderRow {
  id: number;
  order_id: number;
  status: string;
  buyer_name: string;
  phone: string;
  city: string;
  address: string;
  comment: string;
  latitude: number | null;
  longitude: number | null;
  delivery_method: string;
  subtotal: number;
  commission_amount: number;
  seller_payout: number;
  items: OrderItem[];
  created_at: string;
}

export interface Banner {
  id: number;
  title: string;
  image: string;
  target: string;
  is_active: boolean;
  sort_order: number;
}

export interface SellerStats {
  sales_total: number;
  commission_total: number;
  payout_total: number;
  orders_count: number;
  products_count: number;
  rating: number;
  reviews_count: number;
  completion_rate: number;
}

export interface AdminStats {
  orders_count: number;
  sales_total: number;
  commission_total: number;
  payout_total: number;
  customers_count: number;
  sellers_count: number;
  products_count: number;
  popular_products: { id: number; name_ru: string; article: string; sold: number; views: number }[];
}

export interface AdminSeller {
  id: number;
  user_id: number;
  telegram_id: number;
  shop_name: string;
  status: string;
  rating: number;
  orders_count: number;
  products_count: number;
  commission_override: number | null;
}

export interface Review {
  id: number;
  seller_order_id: number;
  seller_id: number;
  stars: number;
  comment: string;
  created_at: string;
}

export interface AnalogReference {
  id: number;
  number: string;
  number_raw: string;
  brand: string;
  is_original: boolean;
}
export interface AnalogGroup {
  id: number;
  title: string;
  references: AnalogReference[];
}
