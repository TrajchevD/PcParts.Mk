import { apiFetch } from "./api";   // <-- adjust path if needed

export async function getUserBuilds() {
  const data = await apiFetch("/api/builder/builds");
  return data.builds ?? data;
}

export async function deleteBuild(id) {
  await apiFetch(`/api/builder/builds/${id}`, { method: "DELETE" });
}

export async function renameBuild(id, name) {
  await apiFetch(`/api/builder/builds/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ name }),
  });
}

export async function createBuild(name = "New Build") {
  return apiFetch("/api/builder/builds", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}