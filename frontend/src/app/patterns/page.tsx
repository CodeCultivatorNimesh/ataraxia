"use client";
import { useState, useEffect } from "react";
import { patternAPI } from "../../lib/api";

const SAMPLE_CANDLES = JSON.stringify([
  {"t":"2024-01-01","o":100,"h":105,"l":98,"c":104,"v":1000},
  {"t":"2024-01-02","o":104,"h":108,"l":102,"c":103,"v":1200},
  {"t":"2024-01-03","o":103,"h":106,"l":99,"c":101,"v":900},
  {"t":"2024-01-04","o":101,"h":102,"l":95,"c":96,"v":1500},
  {"t":"2024-01-05","o":96,"h":100,"l":94,"c":99,"v":1100},
], null, 2);

type Tab = "detect"|"history"|"catalog";

export default function PatternsPage() {
  const [tab, setTab] = useState<Tab>("detect");

  // Detect
  const [symbol, setSymbol] = useState("AAPL");
  const [timeframe, setTimeframe] = useState("1d");
  const [candlesJson, setCandlesJson] = useState(SAMPLE_CANDLES);
  const [currentPrice, setCurrentPrice] = useState(99);
  const [detectResult, setDetectResult] = useState<any>(null);

  // History
  const [histSymbol, setHistSymbol] = useState("AAPL");
  const [histTf, setHistTf] = useState("");
  const [history, setHistory] = useState<any[]>([]);

  // Catalog
  const [catalog, setCatalog] = useState<any>(null);
  const [catalogTab, setCatalogTab] = useState("single");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const detect = async () => {
    setLoading(true); setError(null);
    try {
      const candles = JSON.parse(candlesJson);
      const res = await patternAPI.detect({ symbol, timeframe, candles, current_price: currentPrice });
      setDetectResult(res);
    } catch (e: any) { setError(e.response?.data?.detail || e.message); }
    finally { setLoading(false); }
  };

  const loadHistory = async () => {
    setLoading(true); setError(null);
    try {
      const res = await patternAPI.history(histSymbol, histTf || undefined);
      setHistory(res);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  const loadCatalog = async () => {
    setLoading(true);
    try { const res = await patternAPI.catalog(); setCatalog(res); }
    catch { /* ignore */ }
    finally { setLoading(false); }
  };

  useEffect(() => { if (tab === "catalog" && !catalog) loadCatalog(); }, [tab]);

  const typeColor = (t: string) =>
    t === "bullish" ? "#39ff14" : t === "bearish" ? "#ff4060" : "#8b949e";

  const confBar = (v: number) => (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <div style={{ flex: 1, height: 6, background: "#1c2333", borderRadius: 3, overflow: "hidden" }}>
        <div style={{ width: `${v * 100}%`, height: "100%", background: "#00f5d4", borderRadius: 3 }} />
      </div>
      <span style={{ fontSize: 11, color: "#8b949e", minWidth: 36 }}>{(v * 100).toFixed(0)}%</span>
    </div>
  );

  return (
    <div>
      <h1 className="section-header">Candlestick Patterns</h1>

      <div className="tab-bar">
        <div className={`tab ${tab === "detect" ? "active" : ""}`} onClick={() => setTab("detect")}>Detect Patterns</div>
        <div className={`tab ${tab === "history" ? "active" : ""}`} onClick={() => setTab("history")}>History</div>
        <div className={`tab ${tab === "catalog" ? "active" : ""}`} onClick={() => setTab("catalog")}>Catalog</div>
      </div>

      {/* ─── DETECT ─── */}
      {tab === "detect" && (
        <div className="grid-2">
          <div className="card">
            <div className="card-title">Input</div>
            <div className="field">
              <label className="label">Symbol</label>
              <input className="input" value={symbol} onChange={e => setSymbol(e.target.value.toUpperCase())} />
            </div>
            <div className="field">
              <label className="label">Timeframe</label>
              <select className="input" value={timeframe} onChange={e => setTimeframe(e.target.value)}>
                {["1m","5m","15m","30m","1h","4h","1d","1w"].map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="field">
              <label className="label">Current Price</label>
              <input className="input" type="number" step="any" value={currentPrice} onChange={e => setCurrentPrice(parseFloat(e.target.value) || 0)} />
            </div>
            <div className="field">
              <label className="label">Candles JSON (array of {'{'} o, h, l, c, v, t {'}'})</label>
              <textarea className="input" rows={8} style={{ resize: "vertical", fontFamily: "monospace", fontSize: 11 }}
                value={candlesJson} onChange={e => setCandlesJson(e.target.value)} />
            </div>
            <button className="btn btn-primary" style={{ width: "100%" }} onClick={detect} disabled={loading}>
              {loading ? "Detecting..." : "Detect Patterns"}
            </button>
            {error && <div className="alert-danger" style={{ marginTop: 10 }}>{error}</div>}
          </div>

          <div className="card">
            <div className="card-title">Detection Result</div>
            {!detectResult && <div style={{ color: "#484f58", fontSize: 13 }}>Paste candle data and click Detect.</div>}
            {detectResult && (
              <div>
                {/* Summary row */}
                <div style={{ display: "flex", gap: 10, marginBottom: 16, flexWrap: "wrap" }}>
                  {[
                    { lbl: "Total",    val: detectResult.total_detected, cls: "badge-accent" },
                    { lbl: "Bullish",  val: detectResult.bullish_count,  cls: "badge-green"  },
                    { lbl: "Bearish",  val: detectResult.bearish_count,  cls: "badge-red"    },
                    { lbl: "Neutral",  val: detectResult.neutral_count,  cls: "badge-gray"   },
                  ].map(b => (
                    <div className={`badge ${b.cls}`} key={b.lbl}>{b.lbl}: {b.val}</div>
                  ))}
                  <div className="badge badge-yellow">Bias: {detectResult.bias?.toUpperCase()}</div>
                </div>

                {detectResult.strongest && (
                  <div className="alert-info" style={{ marginBottom: 14 }}>
                    <strong>Strongest:</strong> {detectResult.strongest.pattern_name} ({(detectResult.strongest.confidence * 100).toFixed(0)}% confidence)
                    <div style={{ fontSize: 11, marginTop: 4, color: "#8b949e" }}>{detectResult.strongest.description}</div>
                  </div>
                )}

                {detectResult.patterns?.length > 0 && (
                  <div>
                    <div className="card-title">All Patterns</div>
                    {detectResult.patterns.map((p: any, i: number) => (
                      <div key={i} style={{ padding: "10px 0", borderBottom: "1px solid #1e2d4a22" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                          <span style={{ fontWeight: 700 }}>{p.pattern_name}</span>
                          <span className={`badge ${p.pattern_type === "bullish" ? "badge-green" : p.pattern_type === "bearish" ? "badge-red" : "badge-gray"}`}>
                            {p.pattern_type}
                          </span>
                        </div>
                        {confBar(p.confidence)}
                        <div style={{ fontSize: 11, color: "#484f58", marginTop: 4 }}>{p.description}</div>
                      </div>
                    ))}
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
          <div className="card" style={{ marginBottom: 16 }}>
            <div style={{ display: "flex", gap: 12, alignItems: "flex-end" }}>
              <div style={{ flex: 1 }}>
                <label className="label">Symbol</label>
                <input className="input" value={histSymbol} onChange={e => setHistSymbol(e.target.value.toUpperCase())} />
              </div>
              <div style={{ flex: 1 }}>
                <label className="label">Timeframe (optional)</label>
                <input className="input" value={histTf} onChange={e => setHistTf(e.target.value)} placeholder="1d, 1h …" />
              </div>
              <button className="btn btn-primary" onClick={loadHistory} disabled={loading}>
                {loading ? "Loading..." : "Load History"}
              </button>
            </div>
            {error && <div className="alert-danger" style={{ marginTop: 10 }}>{error}</div>}
          </div>

          <div className="card">
            <div className="card-title">Pattern History — {histSymbol} ({history.length} records)</div>
            {history.length === 0
              ? <div style={{ color: "#484f58", fontSize: 13 }}>No history. Run a detection or load from DB.</div>
              : (
                <table className="table">
                  <thead><tr><th>Pattern</th><th>Type</th><th>Category</th><th>TF</th><th>Confidence</th><th>Detected</th></tr></thead>
                  <tbody>
                    {history.map((h: any) => (
                      <tr key={h.id}>
                        <td style={{ fontWeight: 600 }}>{h.pattern_name}</td>
                        <td><span className="badge" style={{ color: typeColor(h.pattern_type), background: `${typeColor(h.pattern_type)}15` }}>{h.pattern_type}</span></td>
                        <td style={{ color: "#8b949e" }}>{h.category}</td>
                        <td style={{ color: "#8b949e" }}>{h.timeframe}</td>
                        <td>{confBar(h.confidence)}</td>
                        <td style={{ color: "#484f58", fontSize: 11 }}>{new Date(h.detected_at).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
          </div>
        </div>
      )}

      {/* ─── CATALOG ─── */}
      {tab === "catalog" && (
        <div>
          {!catalog && <div style={{ color: "#484f58" }}>Loading catalog...</div>}
          {catalog && (
            <div>
              <div style={{ display: "flex", gap: 12, marginBottom: 16, alignItems: "center", flexWrap: "wrap" }}>
                <div className="badge badge-accent">Total: {catalog.total} patterns</div>
                {["single","double","triple","continuation"].map(t => (
                  <div key={t} className={`tab ${catalogTab === t ? "active" : ""}`}
                    style={{ borderBottom: "none", padding: "6px 14px", borderRadius: 8,
                             background: catalogTab === t ? "rgba(0,245,212,0.1)" : "#1c2333",
                             cursor: "pointer" }}
                    onClick={() => setCatalogTab(t)}>
                    {t.charAt(0).toUpperCase() + t.slice(1)} ({catalog[t]?.length || 0})
                  </div>
                ))}
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 10 }}>
                {catalog[catalogTab]?.map((p: any) => (
                  <div key={p.name} className="card" style={{ padding: "12px 14px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                      <span style={{ fontWeight: 700, fontSize: 13 }}>{p.name}</span>
                      <span className={`badge ${p.type === "bullish" ? "badge-green" : p.type === "bearish" ? "badge-red" : "badge-gray"}`}>
                        {p.type}
                      </span>
                    </div>
                    <div style={{ fontSize: 11, color: "#8b949e", lineHeight: 1.5 }}>{p.desc}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
