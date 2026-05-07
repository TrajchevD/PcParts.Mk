import { apiFetch } from "./api";

export function listBuilds() {
  return apiFetch("/api/builder/builds");
}

export function createBuild(name = "My Build") {
  return apiFetch("/api/builder/builds", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export function getBuild(buildId) {
  return apiFetch(`/api/builder/builds/${buildId}`);
}

export function deleteBuild(buildId) {
  return apiFetch(`/api/builder/builds/${buildId}`, { method: "DELETE" });
}

export function setBuildSlot(buildId, slot, productId) {
  return apiFetch(`/api/builder/builds/${buildId}/slots/${slot}`, {
    method: "PUT",
    body: JSON.stringify({ product_id: productId }),
  });
}

export function getMbSockets() {
  return apiFetch("/api/builder/sockets");
}

export function getOptions(payload) {
  return apiFetch("/api/builder/options", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
