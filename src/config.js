/**
 * API base URL configuration.
 *
 * In development: VITE_API_BASE_URL = "http://localhost:8000"  (set in .env)
 * In production (Vercel): VITE_API_BASE_URL = ""  (empty → uses relative paths like /api/...)
 */
export const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
