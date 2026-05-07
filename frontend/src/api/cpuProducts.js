import { apiFetch } from "./api";

export function fetchCpus({
  search,
  sort = "price_asc",
  limit = 24,
  offset = 0,
  brand,
  socket,
  min_cores,
  min_price,
  max_price,
} = {}) {
  const params = new URLSearchParams();

  if (search) params.append("search", search);
  if (sort) params.append("sort", sort);
  if (limit !== undefined) params.append("limit", limit);
  if (offset !== undefined) params.append("offset", offset);
  if (brand) params.append("brand", brand);
  if (socket) params.append("socket", socket);
  if (min_cores) params.append("min_cores", min_cores);
  if (min_price) params.append("min_price", min_price);
  if (max_price) params.append("max_price", max_price);

  return apiFetch(`/api/products/cpu?${params.toString()}`);
}
export function fetchCpuDetails(cpuModel) {
  return apiFetch(
    `/api/products/cpu/${encodeURIComponent(cpuModel)}`
  );
}