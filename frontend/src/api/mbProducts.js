import { apiFetch } from "./api";

export function fetchMotherboards({
sort = "price_asc",
  limit = 24,
  offset = 0,
  socket,
  memory_type,
  form_factor,
  min_price,
  max_price,
} = {}) {
  const params = new URLSearchParams();

  params.append("sort", sort);
  params.append("limit", limit);
  params.append("offset", offset);

  if (socket) params.append("socket", socket);
  if (memory_type) params.append("memory_type", memory_type);
  if (form_factor) params.append("form_factor", form_factor);
  if (min_price) params.append("min_price", min_price);
  if (max_price) params.append("max_price", max_price);

  return apiFetch(`/api/products/mb?${params.toString()}`);
}

export function fetchMbDetails(productId) {
  return apiFetch(`/api/products/mb/${productId}`);
}
