"use client";
import { useState, useEffect } from "react";
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell, Legend,
} from "recharts";
import { analyticsAPI } from "../../lib/api";

type Tab = "performance"|"equity"|"assets"|"patterns"|"var";

export default function AnalyticsPage() {
  const [tab, setTab] = useState<Tab>("performance");
  const [perf, setPerf] = useState<any>(null);
  const [equity, setEquity] = useState<any[]>([]);
  const [assets, setAssets] = useState<any[]>([]);
  const [patternSummary, setPatternSummary] = useState<any[]>([]);
  const [varData, setVarData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async (fn: () => Promise<any>, setter: (d: any) => void) => {
    setLoading(true); setError(null);
    try { setter(await fn()); }
    catch (e: any) { setError(e.response?.data?.detail || e.message || "Error loading data"); }
    finally { setLoading(false); }
  };

  useEffect(() => {
    if (tab === "performance" && !perf) load(analyticsAPI.performance, setPerf);
    if (tab === "equity" && equity.length === 0) load(() => analyticsAPI.equityCurve().then(r => r.equity_curve || []), setEquity);
    if (tab === "assets" && assets.length === 0) load(analyticsAPI.byAsset, setAssets);
    if (tab === "patterns" && patternSummary.length === 0) load(analyticsAPI.patternSummary, setPatternSummary);
    if (tab === "var" && !varData) load(analyticsAPI.var, setVarData);
  }, [tab]);

  const G = (lbl: string, val: any, color = "#e6edf3") => (
    <div key={lbl} style={{ padding: "8px 0", borderBottom: "1px solid #1e2d4a22", display: "flex", justifyContent: "space-between" }}>
      <span style={{ color: "#8b949e", fontSize: 12 }}>{lbl}</span>
      <span style={{ fontWeight: 700, color }}>{val ?? "—"}</span>
    </div>
  );

  const pnlColor = (v: number) => v >= 0 ? "#39ff14" : "#ff4060";

  return (
    <div>
      <h1 className="section-header">Analytics</h1>

      <div className="tab-bar">
        <div className={`tab ${tab === "performance" ? "active" : ""}`} onClick={() => setTab("performance")}>Performance</div>
        <div className={`tab ${tab === "equity"      ? "active" : ""}`} onClick={() => setTab("equity")}>Equity Curve</div>
        <div className={`tab ${tab === "assets"      ? "active" : ""}`} onClick={() => setTab("assets")}>By Asset</div>
        <div className={`tab ${tab === "patterns"    ? "active" : ""}`} onClick={() => setTab("patterns")}>Pattern Stats</div>
        <div className={`tab ${tab === "var"         ? "active" : ""}`} onClick={() => setTab("var")}>Portfolio VaR</div>
      </div>

      {loading && <div style={{ color: "#8b949e", padding: "1rem 0" }}>Loading...</div>}
      {error && <div className="alert-danger" style={{ marginBottom: 16 }}>{error}</div>}

      {/* ─── PERFORMANCE ─── */}
      {tab === "performance" && perf && (
        <div>
          <div className="grid-4" style={{ marginBottom: 16 }}>
            {[
              { lbl: "Total Trades",   val: perf.total_trades,                 color: "#e6edf3" },
              { lbl: "Win Rate",       val: `${perf.win_rate}%`,               color: perf.win_rate >= 50 ? "#39ff14" : "#ff4060" },
              { lbl: "Profit Factor",  val: perf.profit_factor,                color: perf.profit_factor >= 1.5 ? "#39ff14" : perf.profit_factor >= 1 ? "#ffd60a" : "#ff4060" },
              { lbl: "Expectancy",     val: `$${perf.expectancy}`,             color: perf.expectancy >= 0 ? "#39ff14" : "#ff4060" },
            ].map(c => (
              <div className="metric-card" key={c.lbl}>
                <div className="metric-label">{c.lbl}</div>
                <div className="metric-value" style={{ color: c.color }}>{c.val}</div>
              </div>
            ))}
          </div>

          <div className="grid-2">
            <div className="card">
              <div className="card-title">Trade Statistics</div>
              {G("Total Trades",         perf.total_trades)}
              {G("Winning Trades",       perf.winning_trades, "#39ff14")}
              {G("Losing Trades",        perf.losing_trades,  "#ff4060")}
              {G("Win Rate",             `${perf.win_rate}%`, perf.win_rate >= 50 ? "#39ff14" : "#ff4060")}
              {G("Avg Win",              `$${perf.avg_win}`,  "#39ff14")}
              {G("Avg Loss",             `$${Math.abs(perf.avg_loss)}`, "#ff4060")}
              {G("Largest Win",          `$${perf.largest_win}`,  "#39ff14")}
              {G("Largest Loss",         `$${Math.abs(perf.largest_loss || 0)}`, "#ff4060")}
            </div>
            <div className="card">
              <div className="card-title">Risk Metrics</div>
              {G("Profit Factor",        perf.profit_factor)}
              {G("Sharpe Ratio",         perf.sharpe_ratio)}
              {G("Sortino Ratio",        perf.sortino_ratio)}
              {G("Calmar Ratio",         perf.calmar_ratio)}
              {G("Max Drawdown",         `${perf.max_drawdown_pct}%`, "#ff4060")}
              {G("Avg Drawdown",         `${perf.avg_drawdown_pct}%`)}
              {G("Reward/Risk Ratio",    `${perf.reward_risk_ratio}×`)}
              {G("Expectancy",           `$${perf.expectancy}`, pnlColor(perf.expectancy || 0))}
            </div>
          </div>

          {/* Win/Loss bar chart */}
          {perf.total_trades > 0 && (
            <div className="card" style={{ marginTop: 16 }}>
              <div className="card-title">Win vs Loss</div>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={[{ name: "Wins", value: perf.winning_trades }, { name: "Losses", value: perf.losing_trades }]}>
                  <XAxis dataKey="name" tick={{ fill: "#8b949e", fontSize: 12 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#484f58", fontSize: 10 }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ background: "#161b27", border: "1px solid #1e2d4a", borderRadius: 8, fontSize: 12 }} />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                    <Cell fill="#39ff14" />
                    <Cell fill="#ff4060" />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {/* ─── EQUITY CURVE ─── */}
      {tab === "equity" && equity.length > 0 && (
        <div>
          <div className="card" style={{ marginBottom: 16 }}>
            <div className="card-title">Account Balance Curve</div>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={equity} margin={{ top: 8, right: 0, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="balGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#00f5d4" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#00f5d4" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e2d4a" />
                <XAxis dataKey="date" tick={{ fill: "#484f58", fontSize: 10 }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fill: "#484f58", fontSize: 10 }} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: "#161b27", border: "1px solid #1e2d4a", borderRadius: 8, fontSize: 12 }}
                  labelStyle={{ color: "#8b949e" }} itemStyle={{ color: "#00f5d4" }} />
                <Area type="monotone" dataKey="balance" stroke="#00f5d4" strokeWidth={2}
                  fill="url(#balGrad)" dot={false} name="Balance" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <div className="card-title">Daily P&L</div>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={equity}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e2d4a" />
                <XAxis dataKey="date" tick={{ fill: "#484f58", fontSize: 10 }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fill: "#484f58", fontSize: 10 }} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: "#161b27", border: "1px solid #1e2d4a", borderRadius: 8, fontSize: 12 }}
                  itemStyle={{ color: "#ffd60a" }} />
                <Bar dataKey="daily_pnl" name="Daily P&L" radius={[2,2,0,0]}>
                  {equity.map((e, i) => <Cell key={i} fill={e.daily_pnl >= 0 ? "#39ff14" : "#ff4060"} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
      {tab === "equity" && equity.length === 0 && !loading && (
        <div className="card" style={{ color: "#484f58" }}>No closed trades yet to build an equity curve.</div>
      )}

      {/* ─── BY ASSET ─── */}
      {tab === "assets" && (
        <div>
          {!loading && assets.length === 0 && (
            <div className="card" style={{ color: "#484f58" }}>No closed trades recorded yet.</div>
          )}
          {assets.length > 0 && (
            <div>
              <div className="card" style={{ marginBottom: 16 }}>
                <div className="card-title">P&L by Asset Class</div>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={assets}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e2d4a" />
                    <XAxis dataKey="asset_class" tick={{ fill: "#8b949e", fontSize: 11 }} tickLine={false} axisLine={false} />
                    <YAxis tick={{ fill: "#484f58", fontSize: 10 }} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={{ background: "#161b27", border: "1px solid #1e2d4a", borderRadius: 8, fontSize: 12 }} />
                    <Bar dataKey="total_pnl" name="Total P&L" radius={[4,4,0,0]}>
                      {assets.map((a, i) => <Cell key={i} fill={a.total_pnl >= 0 ? "#39ff14" : "#ff4060"} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="card">
                <div className="card-title">Asset Breakdown</div>
                <table className="table">
                  <thead>
                    <tr><th>Asset</th><th>Trades</th><th>Wins</th><th>Win Rate</th><th>P&L</th><th>Avg P&L</th></tr>
                  </thead>
                  <tbody>
                    {assets.map((a: any) => (
                      <tr key={a.asset_class}>
                        <td style={{ fontWeight: 700, color: "#00f5d4" }}>{a.asset_class}</td>
                        <td>{a.total_trades}</td>
                        <td style={{ color: "#39ff14" }}>{a.winning_trades}</td>
                        <td>{a.win_rate}%</td>
                        <td style={{ fontWeight: 700, color: pnlColor(a.total_pnl) }}>
                          {a.total_pnl >= 0 ? "+" : ""}${a.total_pnl?.toFixed(2)}
                        </td>
                        <td style={{ color: pnlColor(a.avg_pnl) }}>${a.avg_pnl?.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ─── PATTERN STATS ─── */}
      {tab === "patterns" && (
        <div>
          {patternSummary.length === 0 && !loading && (
            <div className="card" style={{ color: "#484f58" }}>No patterns detected yet. Use the Patterns page to run detections.</div>
          )}
          {patternSummary.length > 0 && (
            <div>
              <div className="card" style={{ marginBottom: 16 }}>
                <div className="card-title">Top Patterns by Count</div>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={patternSummary.slice(0, 10)} layout="vertical" margin={{ left: 80, right: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e2d4a" horizontal={false} />
                    <XAxis type="number" tick={{ fill: "#484f58", fontSize: 10 }} axisLine={false} tickLine={false} />
                    <YAxis type="category" dataKey="pattern_name" tick={{ fill: "#8b949e", fontSize: 11 }} axisLine={false} tickLine={false} width={75} />
                    <Tooltip contentStyle={{ background: "#161b27", border: "1px solid #1e2d4a", borderRadius: 8, fontSize: 12 }} />
                    <Bar dataKey="count" name="Count" radius={[0,4,4,0]}>
                      {patternSummary.slice(0,10).map((p: any, i: number) => (
                        <Cell key={i} fill={p.pattern_type === "bullish" ? "#39ff14" : p.pattern_type === "bearish" ? "#ff4060" : "#8b949e"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="card">
                <div className="card-title">Pattern Summary Table</div>
                <table className="table">
                  <thead><tr><th>Pattern</th><th>Type</th><th>Category</th><th>Count</th><th>Avg Confidence</th></tr></thead>
                  <tbody>
                    {patternSummary.map((p: any) => (
                      <tr key={p.pattern_name}>
                        <td style={{ fontWeight: 600 }}>{p.pattern_name}</td>
                        <td>
                          <span className={`badge ${p.pattern_type === "bullish" ? "badge-green" : p.pattern_type === "bearish" ? "badge-red" : "badge-gray"}`}>
                            {p.pattern_type}
                          </span>
                        </td>
                        <td style={{ color: "#8b949e" }}>{p.category}</td>
                        <td style={{ fontWeight: 700, color: "#00f5d4" }}>{p.count}</td>
                        <td>
                          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                            <div style={{ flex: 1, height: 5, background: "#1c2333", borderRadius: 3 }}>
                              <div style={{ width: `${p.avg_confidence * 100}%`, height: "100%", background: "#00f5d4", borderRadius: 3 }} />
                            </div>
                            <span style={{ fontSize: 11, color: "#8b949e" }}>{(p.avg_confidence * 100).toFixed(0)}%</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ─── VaR ─── */}
      {tab === "var" && (
        <div>
          {varData?.error && (
            <div className="alert-warning">{varData.error}</div>
          )}
          {varData && !varData.error && (
            <div className="grid-2">
              <div className="card">
                <div className="card-title">Portfolio VaR (Historical Returns)</div>
                {[
                  ["Historical VaR",          `${varData.historical_var?.toFixed(2)}%`, "#ff4060"],
                  ["Parametric VaR",          `${varData.parametric_var?.toFixed(2)}%`, "#ff8c00"],
                  ["CVaR / Expected Shortfall",`${varData.cvar?.toFixed(2)}%`,          "#ff4060"],
                  ["Mean Return",             `${varData.mean?.toFixed(3)}%`,           "#8b949e"],
                  ["Std Deviation",           `${varData.std?.toFixed(3)}%`,            "#8b949e"],
                  ["Confidence Level",        `${((varData.confidence || 0.95) * 100).toFixed(0)}%`, "#00f5d4"],
                  ["Observations",            varData.n_observations,                   "#8b949e"],
                ].map(([l, v, c]) => G(String(l), v, c as string))}
              </div>
              <div className="card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                <div className="card-title">Interpretation</div>
                <div className="alert-info">
                  With {((varData.confidence || 0.95) * 100).toFixed(0)}% confidence, your maximum expected loss in a single trading period is <strong>{varData.historical_var?.toFixed(2)}%</strong>.
                </div>
                <div className="alert-warning">
                  In the worst {((1 - (varData.confidence || 0.95)) * 100).toFixed(0)}% of cases, average loss would be <strong>{varData.cvar?.toFixed(2)}%</strong> (CVaR).
                </div>
                <div style={{ fontSize: 12, color: "#484f58" }}>
                  Based on {varData.n_observations} closed trades from your journal. Add more trades for a more accurate estimate.
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
