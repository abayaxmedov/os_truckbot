/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE?: string;
  readonly VITE_BACKEND_URL?: string;
  readonly VITE_DEV_TG?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
