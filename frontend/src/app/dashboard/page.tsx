"use client";
import { useEffect, useState } from "react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { analyticsAPI } from "../../lib/api";
import type { DashboardData } from "../../types";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    analyticsAPI.dashboard()
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div style={{ color: "#00f5d4", padding: "2rem" }}>Loading dashboard...</div>;
  if (error) return (
    <div className="alert-danger" style={{ marginTop: "1rem" }}>
      Backend error: {error} — ensure FastAPI is running on port 8000.
    </div>
  );
  if (!data) return null;

  const { account, performance, behavioral, open_trades, top_patterns, equity_curve } = data;
  const S = "$";

  const stateColor = behavioral.state === "healthy" ? "#39ff14"
    : behavioral.state === "moderate" ? "#ffd60a" : "#ff4060";

  return (
    <div>
      <h1 className="section-header">Dashboard</h1>

      {/* Top metric cards */}
      <div className="grid-4" style={{ marginBottom: 16 }}>
        {[
          { label: "Balance",   value: `${S}${account.balance.toLocaleString()}`,     color: "#00f5d4" },
          { label: "Total P&L", value: `${account.total_pnl >= 0 ? "+" : ""}${S}${account.total_pnl}`,
            color: account.total_pnl >= 0 ? "#39ff14" : "#ff4060" },
          { label: "Today P&L", value: `${account.today_pnl >= 0 ? "+" : ""}${S}${account.today_pnl}`,
            color: account.today_pnl >= 0 ? "#39ff14" : "#ff4060" },
          { label: "Daily Loss %", value: `${account.today_loss_pct.toFixed(2)}%`,
            color: account.today_loss_pct > 3 ? "#ff4060" : "#8b949e" },
        ].map(c => (
          <div className="metric-card" key={c.label}>
            <div className="metric-label">{c.label}</div>
            <div className="metric-value" style={{ color: c.color }}>{c.value}</div>
          </div>
        ))}
      </div>

      {/* 2-col row: perf + behavioral */}
      <div className="grid-2" style={{ marginBottom: 16 }}>
        {/* Performance */}
        <div className="card">
          <div className="card-title">Performance</div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px 16px" }}>
            {[
              ["Total Trades",   performance.total_trades],
              ["Win Rate",       `${performance.win_rate}%`],
              ["Profit Factor",  performance.profit_factor],
              ["Sharpe Ratio",   performance.sharpe_ratio],
              ["Avg Win",        `${S}${performance.avg_win}`],
              ["Avg Loss",       `${S}${Math.abs(performance.avg_loss)}`],
              ["Reward/Risk",    `${performance.reward_risk_ratio}×`],
              ["Max Drawdown",   `${performance.max_drawdown_pct}%`],
            ].map(([lbl, val]) => (
              <div key={String(lbl)}>
                <div style={{ fontSize: 10, color: "#484f58", textTransform: "uppercase", letterSpacing: "0.06em" }}>{lbl}</div>
                <div style={{ fontSize: 15, fontWeight: 700, marginTop: 2 }}>{val}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Behavioral state */}
        <div className="card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <div className="card-title">Psychological State</div>
          <div style={{
            padding: "14px 16px",
            borderRadius: 8,
            background: `${stateColor}12`,
            border: `1px solid ${stateColor}30`,
          }}>
            <div style={{ fontSize: 20, fontWeight: 800, color: stateColor, marginBottom: 4 }}>
              {behavioral.state.toUpperCase()}
            </div>
            <div style={{ fontSize: 13, color: "#8b949e" }}>
              Score: <span style={{ color: stateColor, fontWeight: 700 }}>{behavioral.score}/100</span>
            </div>
            <div style={{ fontSize: 13, marginTop: 8, color: behavioral.trading_allowed ? "#39ff14" : "#ff4060", fontWeight: 600 }}>
              {behavioral.trading_allowed ? "✓ Trading Permitted" : "✗ Trading Blocked"}
            </div>
          </div>

          {/* Top patterns */}
          {top_patterns.length > 0 && (
            <div>
              <div className="card-title" style={{ marginBottom: 8 }}>Top Patterns Detected</div>
              {top_patterns.slice(0, 4).map((p, i) => (
                <div key={i} style={{
                  display: "flex", justifyContent: "space-between", alignItems: "center",
                  padding: "5px 0", borderBottom: i < top_patterns.length - 1 ? "1px solid #1e2d4a22" : "none"
                }}>
                  <span style={{ fontSize: 12, color: "#8b949e" }}>{p.pattern}</span>
                  <span className="badge badge-accent">{p.count}×</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Equity Curve */}
      {equity_curve && equity_curve.length > 1 && (
        <div className="card" style={{ marginBottom: 16 }}>
          <div className="card-title">Equity Curve</div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={equity_curve} margin={{ top: 4, right: 0, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="equityGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00f5d4" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#00f5d4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2d4a" />
              <XAxis dataKey="date" tick={{ fill: "#484f58", fontSize: 10 }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fill: "#484f58", fontSize: 10 }} tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{ background: "#161b27", border: "1px solid #1e2d4a", borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: "#8b949e" }}
                itemStyle={{ color: "#00f5d4" }}
              />
              <Area type="monotone" dataKey="balance" stroke="#00f5d4" strokeWidth={2}
                fill="url(#equityGrad)" dot={false} name="Balance" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Open Trades */}
      <div className="card">
        <div className="card-title">Open Trades ({open_trades.length})</div>
        {open_trades.length === 0 ? (
          <div style={{ color: "#484f58", fontSize: 13, padding: "8px 0" }}>No open trades.</div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Symbol</th><th>Dir</th><th>Entry</th><th>Qty</th><th>Asset</th><th>Opened</th>
              </tr>
            </thead>
            <tbody>
              {open_trades.map(t => (
                <tr key={t.id}>
                  <td style={{ fontWeight: 700, color: "#00f5d4" }}>{t.symbol}</td>
                  <td>
                    <span className={`badge ${t.direction === "LONG" ? "badge-green" : "badge-red"}`}>
                      {t.direction}
                    </span>
                  </td>
                  <td>${t.entry_price}</td>
                  <td>{t.quantity}</td>
                  <td style={{ color: "#8b949e" }}>{t.asset_class}</td>
                  <td style={{ color: "#484f58", fontSize: 11 }}>{new Date(t.opened_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
