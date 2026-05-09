import { apiFetch } from "./api";

export function fetchRams({
  search,
  memory_type,
  capacity_gb,
  min_price,
  max_price,
  limit = 24,
  offset = 0,
} = {}) {
  const params = new URLSearchParams();

  if (search) params.append("search", search);
  if (memory_type) params.append("memory_type", memory_type);
  if (capacity_gb) params.append("capacity_gb", capacity_gb);
  if (min_price) params.append("min_price", min_price);
  if (max_price) params.append("max_price", max_price);
  params.append("limit", limit);
  params.append("offset", offset);

  return apiFetch(`/api/products/ram?${params.toString()}`);
}

export function fetchRamDetails(productId) {
  return apiFetch(`/api/products/ram/${productId}`);
}
