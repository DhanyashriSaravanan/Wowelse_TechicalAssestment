const API_URL = (import.meta.env.VITE_API_URL || "").replace(/\/+$/, "");

export async function apiRequest(path, options = {}) {
  if (import.meta.env.PROD && !API_URL) {
    throw new Error("The authentication API is not configured for this site yet.");
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const detail = data.detail;
    const message = Array.isArray(detail)
      ? detail.map(item => item.msg).join(", ")
      : detail || "Something went wrong";
    throw new Error(message);
  }

  return data;
}

export { API_URL };
