import { apiFetch } from "./api";

export function fetchGpus({
  search = null,
  sort = "price_asc",
  limit = 24,
  offset = 0,
  filters = {},
} = {}) {
  const params = new URLSearchParams();

  if (search) params.append("search", search);
  params.append("sort", sort);
  params.append("limit", limit);
  params.append("offset", offset);

  if (filters.brand)     params.append("brand",     filters.brand);
  if (filters.min_vram)  params.append("min_vram",  filters.min_vram);
  if (filters.min_price) params.append("min_price", filters.min_price);
  if (filters.max_price) params.append("max_price", filters.max_price);

  return apiFetch(`/api/products/gpu?${params.toString()}`);
}

export function fetchGpuDetails(model) {
  return apiFetch(`/api/products/gpu/${encodeURIComponent(model)}`);
}
