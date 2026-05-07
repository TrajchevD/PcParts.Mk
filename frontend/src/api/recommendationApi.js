import { apiFetch } from "./api";

export function recommendBuild(budget, profile) {
  return apiFetch("/api/recommend", {
    method: "POST",
    body: JSON.stringify({ budget: Number(budget), profile }),
  });
}
