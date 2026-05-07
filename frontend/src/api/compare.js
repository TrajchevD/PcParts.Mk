import { apiFetch } from "./api";

export function compareParts(category, ids) {
  return apiFetch("/api/compare", {
    method: "POST",
    body: JSON.stringify({
      category,
      ids, // ✅ CHANGE HERE
    }),
  });
}

