import { apiFetch } from "./api";

export function fetchStorage({
  search,
  type,
  capacity_gb,
  sort = "price_asc",
  limit = 24,
  offset = 0,
} = {}) {
  const params = new URLSearchParams();

  if (search) params.append("search", search);
  if (type) params.append("type", type);
  if (capacity_gb) params.append("capacity_gb", capacity_gb);
  params.append("sort", sort);
  params.append("limit", limit);
  params.append("offset", offset);

  return apiFetch(`/api/products/storage?${params.toString()}`);
}

export function fetchStorageDetails(productId) {
  return apiFetch(`/api/products/storage/${productId}`);
}
