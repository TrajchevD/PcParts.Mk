/**
 * Legacy product API used by the old Category page.
 * Maps the old /api/products?category=X pattern to the new category-specific endpoints.
 */
import { apiFetch } from "./api";

const CATEGORY_SLUG_MAP = {
  cpu: "/api/products/cpu",
  gpu: "/api/products/gpu",
  mb: "/api/products/mb",
  ram: "/api/products/ram",
  storage: "/api/products/storage",
};

export function fetchCategories() {
  // Return a static list — the old /api/categories endpoint no longer exists
  return Promise.resolve([
    { slug: "cpu", label: "CPU" },
    { slug: "gpu", label: "GPU" },
    { slug: "mb", label: "Motherboard" },
    { slug: "ram", label: "RAM" },
    { slug: "storage", label: "Storage" },
  ]);
}

export function fetchProducts(params) {
  const base = CATEGORY_SLUG_MAP[params.category];
  if (!base) return Promise.reject(new Error(`Unknown category: ${params.category}`));

  const qs = new URLSearchParams();
  if (params.q) qs.set("search", params.q);
  if (params.price_min != null && params.price_min !== "") qs.set("min_price", params.price_min);
  if (params.price_max != null && params.price_max !== "") qs.set("max_price", params.price_max);
  qs.set("sort", params.sort || "price_asc");
  qs.set("offset", ((Number(params.page || 1) - 1) * Number(params.limit || 24)).toString());
  qs.set("limit", String(params.limit || 24));

  return apiFetch(`${base}?${qs.toString()}`).then(items => ({
    items: Array.isArray(items) ? items : [],
    total: Array.isArray(items) ? items.length : 0,
    pages: 1,
  }));
}
