"use client";
import { useState } from "react";
import { positionAPI } from "../../lib/api";

type Tab = "spot" | "cross" | "isolated";

const INIT_SPOT = { account_balance: 10000, risk_pct: 1.0, entry_price: 150, atr_value: 3.5, direction: "long", volatility: "medium", asset_type: "stock" };
const INIT_CROSS = { account_balance: 10000, entry_price: 40000, atr_value: 800, volatility: "medium", direction: "long", maintenance_margin_pct: 0.5 };
const INIT_ISO   = { account_balance: 10000, entry_price: 40000, atr_value: 800, volatility: "medium", direction: "long", open_positions: 0 };

export default function PositionPage() {
  const [tab, setTab] = useState<Tab>("spot");
  const [spotForm, setSpotForm]   = useState({ ...INIT_SPOT });
  const [crossForm, setCrossForm] = useState({ ...INIT_CROSS });
  const [isoForm, setIsoForm]     = useState({ ...INIT_ISO });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    setLoading(true); setError(null); setResult(null);
    try {
      let res;
      if (tab === "spot")     res = await positionAPI.spot(spotForm);
      else if (tab === "cross") res = await positionAPI.cryptoCross(crossForm);
      else                    res = await positionAPI.cryptoIsolated(isoForm);
      setResult(res);
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message);
    } finally { setLoading(false); }
  };

  const F = (label: string, key: string, form: any, setForm: any, type = "number", step?: string) => (
    <div className="field" key={key}>
      <label className="label">{label}</label>
      <input className="input" type={type} step={step || (type === "number" ? "any" : undefined)}
        value={form[key]} onChange={e => setForm({ ...form, [key]: type === "number" ? parseFloat(e.target.value) || 0 : e.target.value })} />
    </div>
  );

  const Sel = (label: string, key: string, opts: string[], form: any, setForm: any) => (
    <div className="field" key={key}>
      <label className="label">{label}</label>
      <select className="input" value={form[key]} onChange={e => setForm({ ...form, [key]: e.target.value })}>
        {opts.map(o => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  );

  return (
    <div>
      <h1 className="section-header">Position Sizing</h1>

      <div className="tab-bar">
        {(["spot","cross","isolated"] as Tab[]).map(t => (
          <div key={t} className={`tab ${tab === t ? "active" : ""}`} onClick={() => { setTab(t); setResult(null); }}>
            {t === "spot" ? "Spot / Stock" : t === "cross" ? "Crypto Futures — Cross" : "Crypto Futures — Isolated"}
          </div>
        ))}
      </div>

      <div className="grid-2">
        {/* Form */}
        <div className="card">
          <div className="card-title">
            {tab === "spot" ? "Spot / Stock Parameters" : tab === "cross" ? "Cross Futures Parameters" : "Isolated Futures Parameters"}
          </div>

          {tab === "spot" && <>
            {F("Account Balance ($)", "account_balance", spotForm, setSpotForm)}
            {F("Risk % per Trade", "risk_pct", spotForm, setSpotForm, "number", "0.1")}
            {F("Entry Price ($)", "entry_price", spotForm, setSpotForm)}
            {F("ATR Value", "atr_value", spotForm, setSpotForm)}
            {Sel("Direction", "direction", ["long","short"], spotForm, setSpotForm)}
            {Sel("Volatility", "volatility", ["low","medium","high","extreme"], spotForm, setSpotForm)}
            {Sel("Asset Type", "asset_type", ["stock","crypto","forex","futures"], spotForm, setSpotForm)}
          </>}

          {tab === "cross" && <>
            {F("Account Balance ($)", "account_balance", crossForm, setCrossForm)}
            {F("Entry Price ($)", "entry_price", crossForm, setCrossForm)}
            {F("ATR Value", "atr_value", crossForm, setCrossForm)}
            {F("Maintenance Margin %", "maintenance_margin_pct", crossForm, setCrossForm, "number", "0.1")}
            {Sel("Direction", "direction", ["long","short"], crossForm, setCrossForm)}
            {Sel("Volatility", "volatility", ["low","medium","high","extreme"], crossForm, setCrossForm)}
          </>}

          {tab === "isolated" && <>
            {F("Account Balance ($)", "account_balance", isoForm, setIsoForm)}
            {F("Entry Price ($)", "entry_price", isoForm, setIsoForm)}
            {F("ATR Value", "atr_value", isoForm, setIsoForm)}
            {F("Open Positions", "open_positions", isoForm, setIsoForm)}
            {Sel("Direction", "direction", ["long","short"], isoForm, setIsoForm)}
            {Sel("Volatility", "volatility", ["low","medium","high","extreme"], isoForm, setIsoForm)}
          </>}

          <button className="btn btn-primary" style={{ width: "100%", marginTop: 4 }} onClick={submit} disabled={loading}>
            {loading ? "Calculating..." : "Calculate Position Size"}
          </button>
          {error && <div className="alert-danger" style={{ marginTop: 12 }}>{error}</div>}
        </div>

        {/* Result */}
        <div className="card">
          <div className="card-title">Result</div>
          {!result && <div style={{ color: "#484f58", fontSize: 13 }}>Fill in the form and click Calculate.</div>}
          {result && (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {[
                ["Position Size",      result.position_size, result.unit || "units"],
                ["Risk Amount",        `$${result.risk_amount}`, ""],
                ["Stop Loss Price",    `$${result.stop_loss_price}`, ""],
                ["ATR Stop Distance",  result.atr_stop_distance, "pts"],
                ["ATR Multiplier",     `${result.atr_multiplier}×`, ""],
                ["Volatility Regime",  result.volatility, ""],
                ["Direction",          result.direction, ""],
              ].map(([lbl, val, unit]) => (
                <div key={String(lbl)} style={{
                  display: "flex", justifyContent: "space-between", alignItems: "center",
                  padding: "8px 0", borderBottom: "1px solid #1e2d4a"
                }}>
                  <span style={{ color: "#8b949e", fontSize: 12 }}>{lbl}</span>
                  <span style={{ fontWeight: 700, color: "#00f5d4" }}>
                    {val} {unit && <span style={{ fontSize: 11, color: "#484f58" }}>{unit}</span>}
                  </span>
                </div>
              ))}

              {/* Visual risk bar */}
              {result.risk_amount && result.account_balance && (
                <div style={{ marginTop: 8 }}>
                  <div style={{ fontSize: 11, color: "#484f58", marginBottom: 4 }}>Risk utilisation</div>
                  <div style={{ height: 8, background: "#1c2333", borderRadius: 4, overflow: "hidden" }}>
                    <div style={{
                      height: "100%",
                      width: `${Math.min(100, (result.risk_amount / (tab === "spot" ? spotForm.account_balance : tab === "cross" ? crossForm.account_balance : isoForm.account_balance)) * 100)}%`,
                      background: "#00f5d4",
                      borderRadius: 4
                    }} />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
