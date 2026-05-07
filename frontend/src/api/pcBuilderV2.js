import { apiFetch } from "./api";

export function getBuildV2(buildId) {
  return apiFetch(`/api/builder/builds/${buildId}`);
}

export function setBuildSlot(buildId, slot, productId) {
  return apiFetch(`/api/builder/builds/${buildId}/slots/${slot}`, {
    method: "PUT",
    body: JSON.stringify({ product_id: productId }),
  });
}

export function removeBuildSlot(buildId, slot) {
  return apiFetch(`/api/builder/builds/${buildId}/slots/${slot}`, {
    method: "PUT",
    body: JSON.stringify({ product_id: null }),
  });
}
