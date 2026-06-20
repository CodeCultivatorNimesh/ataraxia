"use client";
import { useState } from "react";
import { riskAPI } from "../../lib/api";

export default function RiskPage() {
  const [tab, setTab] = useState<"validate"|"var">("validate");

  // Validate form
  const [vForm, setVForm] = useState({ account_balance: 10000, current_daily_loss_pct: 0, risk_pct: 1.5, open_positions: 2, behavioral_score: 80 });
  const [vResult, setVResult] = useState<any>(null);

  // VaR form
  const [returnsText, setReturnsText] = useState("2.1,-1.3,0.8,-2.5,1.4,3.2,-0.5,1.1,-1.8,0.6");
  const [confidence, setConfidence] = useState(0.95);
  const [varResult, setVarResult] = useState<any>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateTrade = async () => {
    setLoading(true); setError(null);
    try {
      const res = await riskAPI.validate(vForm);
      setVResult(res);
    } catch (e: any) { setError(e.response?.data?.detail || e.message); }
    finally { setLoading(false); }
  };

  const calcVar = async () => {
    setLoading(true); setError(null);
    try {
      const returns = returnsText.split(",").map(s => parseFloat(s.trim())).filter(n => !isNaN(n));
      const res = await riskAPI.var({ returns, confidence });
      setVarResult(res);
    } catch (e: any) { setError(e.response?.data?.detail || e.message); }
    finally { setLoading(false); }
  };

  const riskColor = (level: string) =>
    level === "LOW" ? "#39ff14" : level === "MEDIUM" ? "#ffd60a" : level === "HIGH" ? "#ff8c00" : "#ff4060";

  return (
    <div>
      <h1 className="section-header">Risk Engine</h1>

      <div className="tab-bar">
        <div className={`tab ${tab === "validate" ? "active" : ""}`} onClick={() => setTab("validate")}>Trade Validator</div>
        <div className={`tab ${tab === "var" ? "active" : ""}`} onClick={() => setTab("var")}>Value at Risk (VaR)</div>
      </div>

      {tab === "validate" && (
        <div className="grid-2">
          <div className="card">
            <div className="card-title">Trade Parameters</div>

            {[
              ["Account Balance ($)", "account_balance"],
              ["Daily Loss So Far (%)", "current_daily_loss_pct"],
              ["Trade Risk (%)", "risk_pct"],
              ["Open Positions", "open_positions"],
              ["Behavioral Score (0-100)", "behavioral_score"],
            ].map(([lbl, key]) => (
              <div className="field" key={key}>
                <label className="label">{lbl}</label>
                <input className="input" type="number" step="any"
                  value={vForm[key as keyof typeof vForm]}
                  onChange={e => setVForm({ ...vForm, [key as keyof typeof vForm]: parseFloat(e.target.value) || 0 })} />
              </div>
            ))}

            <button className="btn btn-primary" style={{ width: "100%" }} onClick={validateTrade} disabled={loading}>
              {loading ? "Validating..." : "Validate Trade"}
            </button>
            {error && <div className="alert-danger" style={{ marginTop: 10 }}>{error}</div>}
          </div>

          <div className="card">
            <div className="card-title">Validation Result</div>
            {!vResult && <div style={{ color: "#484f58", fontSize: 13 }}>Click Validate Trade to see results.</div>}
            {vResult && (
              <div>
                {/* Verdict banner */}
                <div className={`alert-banner ${vResult.approved ? "alert-success" : "alert-danger"}`} style={{ marginBottom: 16, fontSize: 15 }}>
                  {vResult.approved ? "✓ TRADE APPROVED" : "✗ TRADE REJECTED"}
                  <div style={{ fontSize: 12, fontWeight: 400, marginTop: 4 }}>{vResult.reason}</div>
                </div>

                <div style={{
                  display: "inline-flex", alignItems: "center", gap: 8, marginBottom: 16,
                  padding: "6px 14px", borderRadius: 999, fontSize: 12, fontWeight: 700,
                  background: `${riskColor(vResult.risk_level)}15`,
                  border: `1px solid ${riskColor(vResult.risk_level)}40`,
                  color: riskColor(vResult.risk_level)
                }}>
                  Risk Level: {vResult.risk_level}
                </div>

                {/* Rule checks */}
                <div className="card-title">Rule Checks</div>
                {vResult.checks?.map((c: any, i: number) => (
                  <div key={i} style={{
                    display: "flex", alignItems: "flex-start", gap: 10, padding: "8px 0",
                    borderBottom: "1px solid #1e2d4a22"
                  }}>
                    <span style={{ fontSize: 14, marginTop: 1 }}>{c.passed ? "✅" : "❌"}</span>
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 600, color: c.passed ? "#e6edf3" : "#ff4060" }}>{c.rule}</div>
                      <div style={{ fontSize: 11, color: "#8b949e", marginTop: 2 }}>{c.detail}</div>
                      {c.fail_reason && <div style={{ fontSize: 11, color: "#ff4060", marginTop: 2 }}>{c.fail_reason}</div>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {tab === "var" && (
        <div className="grid-2">
          <div className="card">
            <div className="card-title">Historical Returns</div>
            <div className="field">
              <label className="label">Returns (comma-separated %)</label>
              <textarea className="input" rows={6} style={{ resize: "vertical" }}
                value={returnsText} onChange={e => setReturnsText(e.target.value)}
                placeholder="2.1, -1.3, 0.8, -2.5, 1.4, ..." />
            </div>
            <div className="field">
              <label className="label">Confidence Level</label>
              <select className="input" value={confidence} onChange={e => setConfidence(parseFloat(e.target.value))}>
                <option value={0.90}>90%</option>
                <option value={0.95}>95%</option>
                <option value={0.99}>99%</option>
              </select>
            </div>
            <button className="btn btn-primary" style={{ width: "100%" }} onClick={calcVar} disabled={loading}>
              {loading ? "Calculating..." : "Calculate VaR"}
            </button>
            {error && <div className="alert-danger" style={{ marginTop: 10 }}>{error}</div>}
          </div>

          <div className="card">
            <div className="card-title">VaR Result</div>
            {!varResult && <div style={{ color: "#484f58", fontSize: 13 }}>Enter returns and click Calculate VaR.</div>}
            {varResult && (
              <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                {[
                  ["Historical VaR", `${varResult.historical_var?.toFixed(2)}%`, "#ff4060"],
                  ["Parametric VaR", `${varResult.parametric_var?.toFixed(2)}%`, "#ff8c00"],
                  ["CVaR (Expected Shortfall)", `${varResult.cvar?.toFixed(2)}%`, "#ff4060"],
                  ["Mean Return", `${varResult.mean?.toFixed(2)}%`, "#8b949e"],
                  ["Std Deviation", `${varResult.std?.toFixed(2)}%`, "#8b949e"],
                  ["Confidence Level", `${(varResult.confidence * 100).toFixed(0)}%`, "#00f5d4"],
                  ["Sample Size", varResult.n_observations, "#8b949e"],
                ].map(([lbl, val, color]) => (
                  <div key={String(lbl)} style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid #1e2d4a" }}>
                    <span style={{ fontSize: 12, color: "#8b949e", paddingBottom: 8 }}>{lbl}</span>
                    <span style={{ fontWeight: 700, color: color as string }}>{val}</span>
                  </div>
                ))}
                <div className="alert-info" style={{ fontSize: 12 }}>
                  With {(confidence * 100).toFixed(0)}% confidence, max loss will not exceed <strong>{varResult.historical_var?.toFixed(2)}%</strong> in a single period.
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
