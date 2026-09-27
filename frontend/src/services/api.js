/**
 * api.js
 * ------
 * Centralized API client. All REST calls to the Flask backend go through
 * here, so the base URL and auth-token handling live in exactly one place.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.PROD
    ? "https://goodfood-studio-api.vercel.app"
    : "http://localhost:5000");

function getToken() {
  return localStorage.getItem("access_token");
}

export function setToken(token) {
  if (token) localStorage.setItem("access_token", token);
}

export function clearToken() {
  localStorage.removeItem("access_token");
}

async function request(path, { method = "GET", body, isForm = false } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (!isForm && body) headers["Content-Type"] = "application/json";

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: isForm ? body : body ? JSON.stringify(body) : undefined,
  });

  const contentType = res.headers.get("content-type") || "";
  const data = contentType.includes("application/json")
    ? await res.json()
    : await res.blob();

  if (!res.ok) {
    const message = (data && data.error) || `Request failed (${res.status})`;
    throw new Error(message);
  }
  return data;
}
export async function downloadAuthedFile(url, filename) {
  const token = getToken();
  const res = await fetch(url, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) throw new Error("Download failed");
  const blob = await res.blob();
  const blobUrl = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = blobUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(blobUrl);
}
export const api = {
  register: (name, email, password) =>
    request("/register", { method: "POST", body: { name, email, password } }),
  login: (email, password) =>
    request("/login", { method: "POST", body: { email, password } }),
  logout: () => request("/logout", { method: "POST" }),

  getProfile: () => request("/profile"),
  updateProfile: (fields) =>
    request("/profile", { method: "PUT", body: fields }),

  generatePlan: (dietary_preference, goal) =>
    request("/generate-plan", {
      method: "POST",
      body: { dietary_preference, goal },
    }),
  listPlans: () => request("/plans"),
  getPlan: (planId) => request(`/plans/${planId}`),
  deletePlan: (planId) => request(`/plans/${planId}`, { method: "DELETE" }),

  listFiles: () => request("/files"),
  uploadFile: (file) => {
    const form = new FormData();
    form.append("file", file);
    return request("/upload", { method: "POST", body: form, isForm: true });
  },
  deleteFile: (fileId) => request(`/files/${fileId}`, { method: "DELETE" }),
  downloadUrl: (fileId) => `${BASE_URL}/files/${fileId}/download`,
  exportPlanUrl: (planId) => `${BASE_URL}/plans/${planId}/export`,
};

export { BASE_URL };
