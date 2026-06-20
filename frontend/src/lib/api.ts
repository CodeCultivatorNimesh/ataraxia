/**
 * API client — all calls to the FastAPI backend.
 */
import axios from "axios";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: BASE,
  headers: { "Content-Type": "application/json" },
});

export const positionAPI = {
  spot:           (data: object) => api.post("/position/spot", data).then(r => r.data),
  cryptoCross:    (data: object) => api.post("/position/crypto-futures/cross", data).then(r => r.data),
  cryptoIsolated: (data: object) => api.post("/position/crypto-futures/isolated", data).then(r => r.data),
};

export const riskAPI = {
  validate: (data: object) => api.post("/risk/validate", data).then(r => r.data),
  var:      (data: object) => api.post("/risk/var", data).then(r => r.data),
};

export const patternAPI = {
  detect:       (data: object) => api.post("/patterns/detect", data).then(r => r.data),
  history:      (symbol: string, tf?: string) =>
    api.get(`/patterns/history/${symbol}`, { params: { timeframe: tf } }).then(r => r.data),
  unreadAlerts: () => api.get("/patterns/alerts/unread").then(r => r.data),
  catalog:      () => api.get("/patterns/catalog").then(r => r.data),
};

export const journalAPI = {
  createTrade: (data: object) => api.post("/journal/trade", data).then(r => r.data),
  closeTrade:  (id: number, exitPrice: number) =>
    api.patch(`/journal/trade/${id}/close`, null, { params: { exit_price: exitPrice } }).then(r => r.data),
  getTrades:   (isOpen?: boolean) =>
    api.get("/journal/trades", { params: { is_open: isOpen } }).then(r => r.data),
  createEntry: (data: object) => api.post("/journal/entry", data).then(r => r.data),
  getEntries:  () => api.get("/journal/entries").then(r => r.data),
};

export const behavioralAPI = {
  analyze:  (data: object) => api.post("/behavioral/analyze", data).then(r => r.data),
  decision: (data: object) => api.post("/behavioral/decision", data).then(r => r.data),
  history:  () => api.get("/behavioral/history").then(r => r.data),
};

export const brokerAPI = {
  account:    (broker: string) => api.get(`/broker/account/${broker}`).then(r => r.data),
  positions:  (broker: string) => api.get(`/broker/positions/${broker}`).then(r => r.data),
  price:      (broker: string, symbol: string) =>
    api.get(`/broker/price/${broker}/${symbol}`).then(r => r.data),
  candles:    (broker: string, symbol: string, tf = "1d", limit = 50) =>
    api.get(`/broker/candles/${broker}/${symbol}`, { params: { timeframe: tf, limit } }).then(r => r.data),
  atr:        (data: object) => api.post("/broker/atr", data).then(r => r.data),
  order:      (data: object) => api.post("/broker/order", data).then(r => r.data),
  crossCheck: () => api.get("/broker/futures/cross-check").then(r => r.data),
  isoSlots:   () => api.get("/broker/futures/isolated-slots").then(r => r.data),
};

export const analyticsAPI = {
  dashboard:      () => api.get("/analytics/dashboard").then(r => r.data),
  performance:    () => api.get("/analytics/performance").then(r => r.data),
  equityCurve:    () => api.get("/analytics/performance/equity-curve").then(r => r.data),
  byAsset:        () => api.get("/analytics/performance/by-asset").then(r => r.data),
  var:            () => api.get("/analytics/var").then(r => r.data),
  patternSummary: () => api.get("/analytics/patterns/summary").then(r => r.data),
};

export default api;
