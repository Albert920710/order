import { defineStore } from "pinia";
import axios from "axios";

const TOKEN_KEY = "sales-token";
const EXPIRES_KEY = "sales-token-exp";

const parsePayload = (token) => {
  try {
    const base64 = token.split(".")[1];
    return JSON.parse(atob(base64));
  } catch (error) {
    return {};
  }
};

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || "",
    expiresAt: Number(localStorage.getItem(EXPIRES_KEY) || 0)
  }),
  getters: {
    isAuthenticated: (state) => state.token && Date.now() < state.expiresAt,
    role: (state) => parsePayload(state.token).role || "sales",
    username: (state) => parsePayload(state.token).sub || ""
  },
  actions: {
    async login(username, password) {
      const form = new URLSearchParams();
      form.append("username", username);
      form.append("password", password);
      const { data } = await axios.post("/api/auth/login", form);
      this.token = data.access_token;
      this.expiresAt = Date.now() + 1000 * 60 * 60 * 24 * 30;
      localStorage.setItem(TOKEN_KEY, this.token);
      localStorage.setItem(EXPIRES_KEY, String(this.expiresAt));
    },
    logout() {
      this.token = "";
      this.expiresAt = 0;
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(EXPIRES_KEY);
    }
  }
});
