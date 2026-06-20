/**
 * WebSocket hook — real-time alerts and dashboard updates.
 */
import { useEffect, useRef, useCallback } from "react";
import { useStore } from "../store";

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/api/v1/ws";

export function usePatternAlerts(symbol?: string) {
  const ws = useRef<WebSocket | null>(null);
  const addAlert = useStore((s) => s.addAlert);

  const connect = useCallback(() => {
    const url = symbol ? `${WS_BASE}/alerts?symbol=${symbol}` : `${WS_BASE}/alerts`;
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      console.log("Pattern alert WebSocket connected");
    };

    ws.current.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "pattern_alert") {
          addAlert(msg.data);
        }
      } catch (e) {
        console.error("WS parse error", e);
      }
    };

    ws.current.onclose = () => {
      // Reconnect after 3s
      setTimeout(connect, 3000);
    };
  }, [symbol, addAlert]);

  useEffect(() => {
    connect();
    return () => ws.current?.close();
  }, [connect]);

  const ping = () => ws.current?.send("ping");
  return { ping };
}

export function useDashboardWS() {
  const ws = useRef<WebSocket | null>(null);
  const setDashboard = useStore((s) => s.setDashboard);

  useEffect(() => {
    ws.current = new WebSocket(`${WS_BASE}/dashboard`);

    ws.current.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "dashboard_update") {
          setDashboard(msg.data);
        }
      } catch (e) {
        console.error("Dashboard WS error", e);
      }
    };

    return () => ws.current?.close();
  }, [setDashboard]);
}
