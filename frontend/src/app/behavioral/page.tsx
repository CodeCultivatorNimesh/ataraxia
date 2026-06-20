"use client";
import { useState, useEffect } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from "recharts";
import { behavioralAPI } from "../../lib/api";

type Tab = "analyze"|"decision"|"history";

const INIT_ANALYZE = { stress_level: 5, sleep_hours: 7, daily_loss_pct: 0, trade_limit: 20 };
const INIT_DECISION = { behavioral_score: 80, daily_loss_pct: 0, consecutive_losses: 0, stress_level: 5, sleep_hours: 7 };

export default function BehavioralPage() {
  const [tab, setTab] = useState<Tab>("analyze");
  const [aForm, setAForm] = useState({ ...INIT_ANALYZE });
  const [dForm, setDForm] = useState({ ...INIT_DECISION });
  const [aResult, setAResult] = useState<any>(null);
  const [dResult, setDResult] = useState<any>(null);
  const [histData, setHistData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = async () => {
    setLoading(true); setError(null);
    try { setAResult(await behavioralAPI.analyze(aForm)); }
    catch (e: any) { setError(e.response?.data?.detail || e.message); }
    finally { setLoading(false); }
  };

  const decide = async () => {
    setLoading(true); setError(null);
    try { setDResult(await behavioralAPI.decision(dForm)); }
    catch (e: any) { setError(e.response?.data?.detail || e.message); }
    finally { setLoading(false); }
  };

  const loadHistory = async () => {
    setLoading(true);
    try { setHistData(await behavioralAPI.history()); }
    catch { /* ignore */ }
    finally { setLoading(false); }
  };

  useEffect(() => { if (tab === "history") loadHistory(); }, [tab]);

  const scoreColor = (s: number) => s >= 70 ? "#39ff14" : s >= 40 ? "#ffd60a" : "#ff4060";
  const severityColor = (s: string) => s === "low" ? "#8b949e" : s === "medium" ? "#ffd60a" : "#ff4060";

  const Slider = (lbl: string, key: string, min: number, max: number, step: number, form: any, setForm: any, unit = "") => (
    <div className="field" key={key}>
      <label className="label">{lbl}</label>
      <input type="range" min={min} max={max} step={step} value={form[key]}
        onChange={e => setForm({ ...form, [key]: parseFloat(e.target.value) })}
        className="input" style={{ padding: "4px 0", accentColor: "#00f5d4" }} />
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "#8b949e", marginTop: 3 }}>
        <span>{min}{unit}</span>
        <span style={{ color: "#00f5d4", fontWeight: 700 }}>{form[key]}{unit}</span>
        <span>{max}{unit}</span>
      </div>
    </div>
  );

  return (
    <div>
      <h1 className="section-header">Behavioral Analysis</h1>

      <div className="tab-bar">
        <div className={`tab ${tab === "analyze" ? "active" : ""}`} onClick={() => setTab("analyze")}>Analyze Behavior</div>
        <div className={`tab ${tab === "decision" ? "active" : ""}`} onClick={() => setTab("decision")}>Trade Decision</div>
        <div className={`tab ${tab === "history" ? "active" : ""}`} onClick={() => setTab("history")}>Score History</div>
      </div>

      {/* ─── ANALYZE ─── */}
      {tab === "analyze" && (
        <div className="grid-2">
          <div className="card">
            <div className="card-title">Current State Inputs</div>
            {Slider("Stress Level", "stress_level", 1, 10, 1, aForm, setAForm, "/10")}
            {Slider("Sleep Hours", "sleep_hours", 0, 12, 0.5, aForm, setAForm, "h")}
            {Slider("Daily Loss %", "daily_loss_pct", 0, 20, 0.5, aForm, setAForm, "%")}
            <div className="field">
              <label className="label">Recent Trades to Analyze</label>
              <input className="input" type="number" value={aForm.trade_limit}
                onChange={e => setAForm({ ...aForm, trade_limit: parseInt(e.target.value) || 20 })} />
            </div>
            <button className="btn btn-primary" style={{ width: "100%" }} onClick={analyze} disabled={loading}>
              {loading ? "Analyzing..." : "Run Analysis"}
            </button>
            {error && <div className="alert-danger" style={{ marginTop: 10 }}>{error}</div>}
          </div>

          <div className="card">
            <div className="card-title">Analysis Result</div>
            {!aResult && <div style={{ color: "#484f58", fontSize: 13 }}>Click Run Analysis to evaluate your trading behavior.</div>}
            {aResult && (
              <div>
                {/* Big score */}
                <div style={{
                  textAlign: "center", marginBottom: 16, padding: "16px",
                  background: `${scoreColor(aResult.behavioral_score)}10`,
                  border: `1px solid ${scoreColor(aResult.behavioral_score)}25`,
                  borderRadius: 10,
                }}>
                  <div style={{ fontSize: 42, fontWeight: 800, color: scoreColor(aResult.behavioral_score) }}>
                    {aResult.behavioral_score}
                  </div>
                  <div style={{ fontSize: 11, color: "#8b949e", textTransform: "uppercase", letterSpacing: "0.1em" }}>Behavioral Score</div>
                </div>

                {/* Boolean flags */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 16 }}>
                  {[
                    ["Revenge Trading",  aResult.insights?.revenge_trading],
                    ["Overtrading",      aResult.insights?.overtrading],
                    ["Loss Aversion",    aResult.insights?.loss_aversion],
                    ["Overconfidence",   aResult.insights?.overconfidence],
                    ["Recency Bias",     aResult.insights?.recency_bias],
                  ].map(([lbl, val]) => (
                    <div key={String(lbl)} style={{
                      padding: "8px 10px", borderRadius: 8,
                      background: val ? "rgba(255,64,96,0.08)" : "rgba(57,255,20,0.05)",
                      border: `1px solid ${val ? "rgba(255,64,96,0.2)" : "rgba(57,255,20,0.1)"}`,
                    }}>
                      <div style={{ fontSize: 10, color: "#8b949e", textTransform: "uppercase", marginBottom: 2 }}>{lbl}</div>
                      <div style={{ fontWeight: 700, color: val ? "#ff4060" : "#39ff14" }}>{val ? "DETECTED" : "CLEAR"}</div>
                    </div>
                  ))}
                </div>

                {/* Biases */}
                {aResult.biases?.length > 0 && (
                  <div>
                    <div className="card-title">Detected Biases</div>
                    {aResult.biases.map((b: any, i: number) => (
                      <div key={i} style={{ padding: "8px 0", borderBottom: "1px solid #1e2d4a22" }}>
                        <div style={{ display: "flex", justifyContent: "space-between" }}>
                          <span style={{ fontWeight: 600, fontSize: 13 }}>{b.bias}</span>
                          <span style={{ fontSize: 11, fontWeight: 700, color: severityColor(b.severity) }}>
                            {b.severity?.toUpperCase()}
                          </span>
                        </div>
                        <div style={{ fontSize: 11, color: "#8b949e", marginTop: 3 }}>{b.detail}</div>
                      </div>
                    ))}
                  </div>
                )}

                <div style={{ fontSize: 11, color: "#484f58", marginTop: 12 }}>
                  Analyzed {aResult.trade_count} recent trades.
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ─── DECISION ─── */}
      {tab === "decision" && (
        <div className="grid-2">
          <div className="card">
            <div className="card-title">Decision Engine Inputs</div>
            {Slider("Behavioral Score", "behavioral_score", 0, 100, 1, dForm, setDForm)}
            {Slider("Daily Loss %", "daily_loss_pct", 0, 20, 0.5, dForm, setDForm, "%")}
            {Slider("Consecutive Losses", "consecutive_losses", 0, 10, 1, dForm, setDForm)}
            {Slider("Stress Level", "stress_level", 1, 10, 1, dForm, setDForm, "/10")}
            {Slider("Sleep Hours", "sleep_hours", 0, 12, 0.5, dForm, setDForm, "h")}
            <button className="btn btn-primary" style={{ width: "100%" }} onClick={decide} disabled={loading}>
              {loading ? "Evaluating..." : "Get Trade Decision"}
            </button>
            {error && <div className="alert-danger" style={{ marginTop: 10 }}>{error}</div>}
          </div>

          <div className="card">
            <div className="card-title">Decision Result</div>
            {!dResult && <div style={{ color: "#484f58", fontSize: 13 }}>Set your current state and click Get Trade Decision.</div>}
            {dResult && (
              <div>
                <div className={`alert-banner ${dResult.can_trade ? "alert-success" : "alert-danger"}`} style={{ fontSize: 16, marginBottom: 16 }}>
                  {dResult.can_trade ? "✅ CLEARED TO TRADE" : "🚫 TRADING BLOCKED"}
                </div>

                <div style={{ fontSize: 13, color: "#8b949e", marginBottom: 16 }}>{dResult.reason}</div>

                {dResult.warnings?.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <div className="card-title">Warnings</div>
                    {dResult.warnings.map((w: string, i: number) => (
                      <div key={i} className="alert-warning" style={{ marginBottom: 6, fontSize: 12 }}>⚠ {w}</div>
                    ))}
                  </div>
                )}

                {dResult.recommendations?.length > 0 && (
                  <div>
                    <div className="card-title">Recommendations</div>
                    {dResult.recommendations.map((r: string, i: number) => (
                      <div key={i} style={{ padding: "6px 0", borderBottom: "1px solid #1e2d4a22", fontSize: 12, color: "#8b949e" }}>
                        → {r}
                      </div>
                    ))}
                  </div>
                )}

                {dResult.risk_multiplier !== undefined && (
                  <div style={{ marginTop: 14, padding: "10px 14px", background: "#1c2333", borderRadius: 8 }}>
                    <div style={{ fontSize: 11, color: "#484f58", marginBottom: 4 }}>Risk Multiplier</div>
                    <div style={{ fontSize: 20, fontWeight: 700, color: "#00f5d4" }}>{dResult.risk_multiplier}×</div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ─── HISTORY ─── */}
      {tab === "history" && (
        <div>
          {histData.length > 1 && (
            <div className="card" style={{ marginBottom: 16 }}>
              <div className="card-title">Score Over Time</div>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={[...histData].reverse()} margin={{ top: 4, right: 0, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e2d4a" />
                  <XAxis dataKey="recorded_at" tick={{ fill: "#484f58", fontSize: 9 }} tickLine={false} axisLine={false}
                    tickFormatter={v => new Date(v).toLocaleDateString()} />
                  <YAxis domain={[0, 100]} tick={{ fill: "#484f58", fontSize: 10 }} tickLine={false} axisLine={false} />
                  <ReferenceLine y={60} stroke="#39ff14" strokeDasharray="4 4" opacity={0.4} />
                  <ReferenceLine y={40} stroke="#ff4060" strokeDasharray="4 4" opacity={0.4} />
                  <Tooltip contentStyle={{ background: "#161b27", border: "1px solid #1e2d4a", borderRadius: 8, fontSize: 12 }}
                    labelFormatter={v => new Date(v).toLocaleDateString()}
                    itemStyle={{ color: "#00f5d4" }} />
                  <Line type="monotone" dataKey="behavioral_score" stroke="#00f5d4" strokeWidth={2} dot={false} name="Score" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          <div className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <div className="card-title" style={{ marginBottom: 0 }}>History ({histData.length} records)</div>
              <button className="btn btn-ghost" style={{ fontSize: 11 }} onClick={loadHistory}>Refresh</button>
            </div>
            <table className="table">
              <thead><tr><th>Score</th><th>Stress</th><th>Sleep</th><th>Daily Loss</th><th>Revenge</th><th>Overtrade</th><th>Date</th></tr></thead>
              <tbody>
                {histData.map((r: any) => (
                  <tr key={r.id}>
                    <td style={{ fontWeight: 700, color: scoreColor(r.behavioral_score) }}>{r.behavioral_score}</td>
                    <td>{r.stress_level}/10</td>
                    <td>{r.sleep_hours}h</td>
                    <td style={{ color: r.daily_loss_pct > 3 ? "#ff4060" : "#8b949e" }}>{r.daily_loss_pct}%</td>
                    <td style={{ color: r.revenge_trading ? "#ff4060" : "#39ff14" }}>{r.revenge_trading ? "Yes" : "No"}</td>
                    <td style={{ color: r.overtrading ? "#ff4060" : "#39ff14" }}>{r.overtrading ? "Yes" : "No"}</td>
                    <td style={{ color: "#484f58", fontSize: 11 }}>{new Date(r.recorded_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
