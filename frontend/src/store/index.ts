/**
 * Zustand global state store.
 */
import { create } from "zustand";
import type { DashboardData, BehavioralInsights } from "../types";

interface AppState {
  currency:      string;
  currencySymbol: string;
  dashboard:     DashboardData | null;
  behavioral:    BehavioralInsights | null;
  alerts:        any[];
  setCurrency:   (code: string) => void;
  setDashboard:  (data: DashboardData) => void;
  setBehavioral: (data: BehavioralInsights) => void;
  addAlert:      (alert: any) => void;
  clearAlerts:   () => void;
}

const CURRENCY_SYMBOLS: Record<string, string> = {
  USD: "$", EUR: "€", GBP: "£", NPR: "रू", INR: "₹", JPY: "¥",
};

export const useStore = create<AppState>((set) => ({
  currency:       "USD",
  currencySymbol: "$",
  dashboard:      null,
  behavioral:     null,
  alerts:         [],

  setCurrency: (code) => set({
    currency:       code,
    currencySymbol: CURRENCY_SYMBOLS[code] || "$",
  }),

  setDashboard:  (data) => set({ dashboard: data }),
  setBehavioral: (data) => set({ behavioral: data }),

  addAlert: (alert) => set((state) => ({
    alerts: [alert, ...state.alerts].slice(0, 50),
  })),

  clearAlerts: () => set({ alerts: [] }),
}));
