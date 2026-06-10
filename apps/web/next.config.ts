import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

const nextConfig: NextConfig = {
  // Phase 1: minimal config.
  // Later phases will add: rewrites for /api proxy to FastAPI, image domains
  // for Seguin Morris brand assets, and any production hardening.
};

export default withNextIntl(nextConfig);
