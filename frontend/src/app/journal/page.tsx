"use client";
import { useState, useEffect, useCallback } from "react";
import { journalAPI } from "../../lib/api";

type Tab = "new"|"open"|"history"|"notes";

const INIT_TRADE = {
  symbol: "AAPL", asset_class: "STOCK", direction: "LONG", broker: "",
  margin_mode: "NONE", leverage: 1, entry_price: 150, stop_loss: 145,
  take_profit: 160, quantity: 10, risk_amount: 50, risk_pct: 0.5,
  atr_value: 3.5, emotion_score: 70, notes: "", patterns_at_entry: "",
};

const INIT_NOTE = { trade_id: "", emotion_score: 70, pre_trade_notes: "", post_trade_notes: "", auto_notes: "", warnings: "" };

export default function JournalPage() {
  const [tab, setTab] = useState<Tab>("new");
  const [tradeForm, setTradeForm] = useState({ ...INIT_TRADE });
  const [noteForm, setNoteForm] = useState({ ...INIT_NOTE });
  const [openTrades, setOpenTrades] = useState<any[]>([]);
  const [allTrades, setAllTrades] = useState<any[]>([]);
  const [entries, setEntries] = useState<any[]>([]);
  const [closeId, setCloseId] = useState("");
  const [closePrice, setClosePrice] = useState("");
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState<{ type: "success"|"error"; text: string } | null>(null);

  const flash = (type: "success"|"error", text: string) => {
    setMsg({ type, text });
    setTimeout(() => setMsg(null), 3500);
  };

  const loadOpen    = useCallback(async () => { const r = await journalAPI.getTrades(true);  setOpenTrades(r); }, []);
  const loadHistory = useCallback(async () => { const r = await journalAPI.getTrades();      setAllTrades(r); }, []);
  const loadEntries = useCallback(async () => { const r = await journalAPI.getEntries();     setEntries(r); }, []);

  useEffect(() => {
    if (tab === "open") loadOpen();
    if (tab === "history") loadHistory();
    if (tab === "notes") loadEntries();
  }, [tab]);

  const createTrade = async () => {
    setLoading(true);
    try {
      const body: any = { ...tradeForm, broker: tradeForm.broker || null };
      await journalAPI.createTrade(body);
      flash("success", "Trade logged successfully!");
      setTradeForm({ ...INIT_TRADE });
      await loadOpen();
    } catch (e: any) { flash("error", e.response?.data?.detail || e.message); }
    finally { setLoading(false); }
  };

  const closeTrade = async () => {
    if (!closeId || !closePrice) return;
    setLoading(true);
    try {
      const res = await journalAPI.closeTrade(parseInt(closeId), parseFloat(closePrice));
      flash("success", `Trade #${closeId} closed — P&L: $${res.pnl?.toFixed(2)} (${res.pnl_pct?.toFixed(2)}%)`);
      setCloseId(""); setClosePrice("");
      await loadOpen();
    } catch (e: any) { flash("error", e.response?.data?.detail || e.message); }
    finally { setLoading(false); }
  };

  const createNote = async () => {
    setLoading(true);
    try {
      await journalAPI.createEntry({ ...noteForm, trade_id: noteForm.trade_id ? parseInt(noteForm.trade_id) : null });
      flash("success", "Journal entry saved!");
      setNoteForm({ ...INIT_NOTE });
      await loadEntries();
    } catch (e: any) { flash("error", e.response?.data?.detail || e.message); }
    finally { setLoading(false); }
  };

  const TF = (lbl: string, key: string, type = "text", opts?: string[]) => {
    const val = (tradeForm as any)[key];
    return (
      <div className="field" key={key}>
        <label className="label">{lbl}</label>
        {opts
          ? <select className="input" value={val} onChange={e => setTradeForm({ ...tradeForm, [key]: e.target.value })}>
              {opts.map(o => <option key={o} value={o}>{o}</option>)}
            </select>
          : <input className="input" type={type} step={type === "number" ? "any" : undefined} value={val}
              onChange={e => setTradeForm({ ...tradeForm, [key]: type === "number" ? parseFloat(e.target.value) || 0 : e.target.value })} />
        }
      </div>
    );
  };

  const pnlColor = (pnl: number | null) => pnl === null ? "#8b949e" : pnl >= 0 ? "#39ff14" : "#ff4060";

  return (
    <div>
      <h1 className="section-header">Trade Journal</h1>

      {msg && (
        <div className={`alert-banner ${msg.type === "success" ? "alert-success" : "alert-danger"}`} style={{ marginBottom: 16 }}>
          {msg.text}
        </div>
      )}

      <div className="tab-bar">
        {(["new","open","history","notes"] as Tab[]).map(t => (
          <div key={t} className={`tab ${tab === t ? "active" : ""}`} onClick={() => setTab(t)}>
            {t === "new" ? "Log Trade" : t === "open" ? "Open Trades" : t === "history" ? "Trade History" : "Journal Entries"}
          </div>
        ))}
      </div>

      {/* ─── NEW TRADE ─── */}
      {tab === "new" && (
        <div className="grid-2">
          <div className="card">
            <div className="card-title">Trade Details</div>
            {TF("Symbol", "symbol")}
            {TF("Direction", "direction", "text", ["LONG","SHORT"])}
            {TF("Asset Class", "asset_class", "text", ["STOCK","CRYPTO_SPOT","CRYPTO_FUTURES","FUTURES","FOREX"])}
            {TF("Broker (optional)", "broker")}
            {TF("Margin Mode", "margin_mode", "text", ["NONE","CROSS","ISOLATED"])}
            {TF("Leverage", "leverage", "number")}
            {TF("Entry Price ($)", "entry_price", "number")}
            {TF("Stop Loss ($)", "stop_loss", "number")}
            {TF("Take Profit ($)", "take_profit", "number")}
            {TF("Quantity", "quantity", "number")}
          </div>
          <div className="card">
            <div className="card-title">Risk & Psychology</div>
            {TF("Risk Amount ($)", "risk_amount", "number")}
            {TF("Risk %", "risk_pct", "number")}
            {TF("ATR Value", "atr_value", "number")}
            <div className="field">
              <label className="label">Emotion Score (0–100)</label>
              <input className="input" type="range" min={0} max={100} value={tradeForm.emotion_score}
                onChange={e => setTradeForm({ ...tradeForm, emotion_score: parseInt(e.target.value) })}
                style={{ accentColor: "#00f5d4" }} />
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "#8b949e", marginTop: 4 }}>
                <span>Fearful (0)</span>
                <span style={{ fontWeight: 700, color: "#00f5d4" }}>{tradeForm.emotion_score}</span>
                <span>Confident (100)</span>
              </div>
            </div>
            <div className="field">
              <label className="label">Pre-Trade Notes</label>
              <textarea className="input" rows={3} value={tradeForm.notes}
                onChange={e => setTradeForm({ ...tradeForm, notes: e.target.value })} />
            </div>
            <div className="field">
              <label className="label">Patterns at Entry (comma-separated)</label>
              <input className="input" value={tradeForm.patterns_at_entry}
                onChange={e => setTradeForm({ ...tradeForm, patterns_at_entry: e.target.value })}
                placeholder="Hammer, Bullish Engulfing…" />
            </div>
            <button className="btn btn-success" style={{ width: "100%" }} onClick={createTrade} disabled={loading}>
              {loading ? "Saving..." : "Log Trade"}
            </button>
          </div>
        </div>
      )}

      {/* ─── OPEN TRADES ─── */}
      {tab === "open" && (
        <div>
          {/* Close trade widget */}
          <div className="card" style={{ marginBottom: 16 }}>
            <div className="card-title">Close a Trade</div>
            <div style={{ display: "flex", gap: 12, alignItems: "flex-end", flexWrap: "wrap" }}>
              <div>
                <label className="label">Trade ID</label>
                <input className="input" style={{ width: 120 }} type="number" value={closeId}
                  onChange={e => setCloseId(e.target.value)} placeholder="e.g. 3" />
              </div>
              <div>
                <label className="label">Exit Price ($)</label>
                <input className="input" style={{ width: 150 }} type="number" step="any" value={closePrice}
                  onChange={e => setClosePrice(e.target.value)} placeholder="e.g. 162.50" />
              </div>
              <button className="btn btn-danger" onClick={closeTrade} disabled={loading || !closeId || !closePrice}>
                {loading ? "Closing..." : "Close Trade"}
              </button>
            </div>
          </div>

          <div className="card">
            <div className="card-title">Open Positions ({openTrades.length})</div>
            {openTrades.length === 0
              ? <div style={{ color: "#484f58", fontSize: 13 }}>No open trades.</div>
              : (
                <table className="table">
                  <thead><tr><th>ID</th><th>Symbol</th><th>Dir</th><th>Entry</th><th>SL</th><th>TP</th><th>Qty</th><th>Asset</th><th>Opened</th></tr></thead>
                  <tbody>
                    {openTrades.map((t: any) => (
                      <tr key={t.id}>
                        <td style={{ color: "#484f58" }}>#{t.id}</td>
                        <td style={{ fontWeight: 700, color: "#00f5d4" }}>{t.symbol}</td>
                        <td><span className={`badge ${t.direction === "LONG" ? "badge-green" : "badge-red"}`}>{t.direction}</span></td>
                        <td>${t.entry_price}</td>
                        <td style={{ color: "#ff4060" }}>{t.stop_loss ? `$${t.stop_loss}` : "—"}</td>
                        <td style={{ color: "#39ff14" }}>{t.take_profit ? `$${t.take_profit}` : "—"}</td>
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
      )}

      {/* ─── HISTORY ─── */}
      {tab === "history" && (
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <div className="card-title" style={{ marginBottom: 0 }}>All Trades ({allTrades.length})</div>
            <button className="btn btn-ghost" style={{ fontSize: 11 }} onClick={loadHistory}>Refresh</button>
          </div>
          {allTrades.length === 0
            ? <div style={{ color: "#484f58", fontSize: 13 }}>No trades recorded yet.</div>
            : (
              <table className="table">
                <thead><tr><th>ID</th><th>Symbol</th><th>Dir</th><th>Entry</th><th>Exit</th><th>Qty</th><th>P&L</th><th>P&L %</th><th>Status</th><th>Date</th></tr></thead>
                <tbody>
                  {allTrades.map((t: any) => (
                    <tr key={t.id}>
                      <td style={{ color: "#484f58" }}>#{t.id}</td>
                      <td style={{ fontWeight: 700, color: "#00f5d4" }}>{t.symbol}</td>
                      <td><span className={`badge ${t.direction === "LONG" ? "badge-green" : "badge-red"}`}>{t.direction}</span></td>
                      <td>${t.entry_price}</td>
                      <td>{t.exit_price ? `$${t.exit_price}` : "—"}</td>
                      <td>{t.quantity}</td>
                      <td style={{ fontWeight: 700, color: pnlColor(t.pnl) }}>
                        {t.pnl !== null ? `${t.pnl >= 0 ? "+" : ""}$${t.pnl?.toFixed(2)}` : "—"}
                      </td>
                      <td style={{ color: pnlColor(t.pnl) }}>
                        {t.pnl_pct !== null ? `${t.pnl_pct >= 0 ? "+" : ""}${t.pnl_pct?.toFixed(2)}%` : "—"}
                      </td>
                      <td><span className={`badge ${t.is_open ? "badge-yellow" : "badge-gray"}`}>{t.is_open ? "OPEN" : "CLOSED"}</span></td>
                      <td style={{ color: "#484f58", fontSize: 11 }}>{new Date(t.opened_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
        </div>
      )}

      {/* ─── NOTES ─── */}
      {tab === "notes" && (
        <div className="grid-2">
          <div className="card">
            <div className="card-title">New Journal Entry</div>
            <div className="field">
              <label className="label">Trade ID (optional)</label>
              <input className="input" type="number" value={noteForm.trade_id}
                onChange={e => setNoteForm({ ...noteForm, trade_id: e.target.value })} placeholder="Link to trade #…" />
            </div>
            <div className="field">
              <label className="label">Emotion Score</label>
              <input className="input" type="range" min={0} max={100} value={noteForm.emotion_score}
                onChange={e => setNoteForm({ ...noteForm, emotion_score: parseInt(e.target.value) })}
                style={{ accentColor: "#00f5d4" }} />
              <div style={{ textAlign: "center", fontSize: 12, color: "#00f5d4", marginTop: 4 }}>{noteForm.emotion_score}</div>
            </div>
            <div className="field">
              <label className="label">Pre-Trade Notes</label>
              <textarea className="input" rows={3} value={noteForm.pre_trade_notes}
                onChange={e => setNoteForm({ ...noteForm, pre_trade_notes: e.target.value })} />
            </div>
            <div className="field">
              <label className="label">Post-Trade Notes</label>
              <textarea className="input" rows={3} value={noteForm.post_trade_notes}
                onChange={e => setNoteForm({ ...noteForm, post_trade_notes: e.target.value })} />
            </div>
            <div className="field">
              <label className="label">Auto / System Notes</label>
              <textarea className="input" rows={2} value={noteForm.auto_notes}
                onChange={e => setNoteForm({ ...noteForm, auto_notes: e.target.value })} />
            </div>
            <button className="btn btn-primary" style={{ width: "100%" }} onClick={createNote} disabled={loading}>
              {loading ? "Saving..." : "Save Entry"}
            </button>
          </div>
          <div className="card">
            <div className="card-title">Recent Entries ({entries.length})</div>
            {entries.length === 0
              ? <div style={{ color: "#484f58", fontSize: 13 }}>No entries yet.</div>
              : entries.map((e: any) => (
                <div key={e.id} style={{ padding: "12px 0", borderBottom: "1px solid #1e2d4a22" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                    <span style={{ color: "#484f58", fontSize: 11 }}>#{e.id}{e.trade_id ? ` — Trade #${e.trade_id}` : ""}</span>
                    <span style={{ color: "#00f5d4", fontWeight: 700 }}>Score: {e.emotion_score}</span>
                  </div>
                  {e.pre_trade_notes && <div style={{ fontSize: 12, color: "#8b949e", marginBottom: 4 }}><strong>Pre:</strong> {e.pre_trade_notes}</div>}
                  {e.post_trade_notes && <div style={{ fontSize: 12, color: "#8b949e", marginBottom: 4 }}><strong>Post:</strong> {e.post_trade_notes}</div>}
                  {e.auto_notes && <div style={{ fontSize: 11, color: "#484f58" }}>{e.auto_notes}</div>}
                  <div style={{ fontSize: 10, color: "#484f58", marginTop: 4 }}>{new Date(e.created_at).toLocaleString()}</div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
