"use client";
import { useState } from "react";
import { brokerAPI } from "../../lib/api";

type Tab = "account"|"positions"|"order"|"price"|"futures";
type BrokerName = "alpaca"|"binance"|"binance_futures";

const BROKERS: { value: BrokerName; label: string }[] = [
  { value: "alpaca",          label: "Alpaca (Stocks)" },
  { value: "binance",         label: "Binance (Spot)" },
  { value: "binance_futures", label: "Binance Futures" },
];

const INIT_ORDER = {
  broker: "alpaca" as BrokerName, symbol: "AAPL", side: "buy",
  qty: 1, order_type: "market", limit_price: "", leverage: 1, margin_mode: "CROSS",
};

export default function BrokerPage() {
  const [tab, setTab] = useState<Tab>("account");
  const [broker, setBroker] = useState<BrokerName>("alpaca");
  const [account, setAccount] = useState<any>(null);
  const [positions, setPositions] = useState<any[]>([]);
  const [orderForm, setOrderForm] = useState({ ...INIT_ORDER });
  const [orderResult, setOrderResult] = useState<any>(null);
  const [priceSymbol, setPriceSymbol] = useState("AAPL");
  const [priceResult, setPriceResult] = useState<any>(null);
  const [atrForm, setAtrForm] = useState({ broker: "alpaca" as BrokerName, symbol: "AAPL", timeframe: "1d", period: 14 });
  const [atrResult, setAtrResult] = useState<any>(null);
  const [futuresInfo, setFuturesInfo] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const go = async (fn: () => Promise<any>, onDone: (r: any) => void) => {
    setLoading(true); setError(null);
    try { onDone(await fn()); }
    catch (e: any) {
      const msg = e.response?.data?.detail || e.message;
      if (msg.includes("not configured")) setError(`${broker} API keys are not configured in .env`);
      else setError(msg);
    }
    finally { setLoading(false); }
  };

  const loadAccount   = () => go(() => brokerAPI.account(broker),    setAccount);
  const loadPositions = () => go(() => brokerAPI.positions(broker),   setPositions);
  const placeOrder    = () => go(() => brokerAPI.order({
    ...orderForm,
    limit_price: orderForm.limit_price ? parseFloat(orderForm.limit_price) : null,
    leverage: orderForm.leverage || 1,
  }), setOrderResult);
  const fetchPrice    = () => go(() => brokerAPI.price(broker, priceSymbol), setPriceResult);
  const fetchAtr      = () => go(() => brokerAPI.atr(atrForm), setAtrResult);
  const loadFutures   = () => go(() => Promise.all([brokerAPI.crossCheck(), brokerAPI.isoSlots()]),
    ([cross, iso]) => setFuturesInfo({ cross, iso }));

  const OF = (lbl: string, key: keyof typeof orderForm, type = "text", opts?: string[]) => (
    <div className="field" key={key}>
      <label className="label">{lbl}</label>
      {opts
        ? <select className="input" value={orderForm[key] as string}
            onChange={e => setOrderForm({ ...orderForm, [key]: e.target.value as any })}>
            {opts.map(o => <option key={o} value={o}>{o}</option>)}
          </select>
        : <input className="input" type={type} step={type === "number" ? "any" : undefined}
            value={orderForm[key] as string}
            onChange={e => setOrderForm({ ...orderForm, [key]: e.target.value })} />
      }
    </div>
  );

  const unconfiguredBanner = error?.includes("not configured") ? (
    <div className="alert-warning" style={{ marginTop: 10 }}>
      ⚠ {error}<br/>
      <span style={{ fontSize: 11 }}>Add your API keys to <code>.env</code> and restart the backend.</span>
    </div>
  ) : error ? <div className="alert-danger" style={{ marginTop: 10 }}>{error}</div> : null;

  return (
    <div>
      <h1 className="section-header">Broker Bridge</h1>

      <div className="tab-bar">
        <div className={`tab ${tab === "account"   ? "active" : ""}`} onClick={() => setTab("account")}>Account</div>
        <div className={`tab ${tab === "positions" ? "active" : ""}`} onClick={() => setTab("positions")}>Positions</div>
        <div className={`tab ${tab === "order"     ? "active" : ""}`} onClick={() => setTab("order")}>Place Order</div>
        <div className={`tab ${tab === "price"     ? "active" : ""}`} onClick={() => setTab("price")}>Price / ATR</div>
        <div className={`tab ${tab === "futures"   ? "active" : ""}`} onClick={() => setTab("futures")}>Futures Checks</div>
      </div>

      {/* Broker selector (shared) */}
      {tab !== "futures" && tab !== "order" && (
        <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 16 }}>
          <label className="label" style={{ marginBottom: 0 }}>Broker:</label>
          {BROKERS.map(b => (
            <button key={b.value}
              className={`btn ${broker === b.value ? "btn-primary" : "btn-ghost"}`}
              style={{ fontSize: 12, padding: "5px 14px" }}
              onClick={() => { setBroker(b.value); setAccount(null); setPositions([]); setError(null); }}>
              {b.label}
            </button>
          ))}
        </div>
      )}

      {/* ─── ACCOUNT ─── */}
      {tab === "account" && (
        <div>
          <button className="btn btn-primary" onClick={loadAccount} disabled={loading} style={{ marginBottom: 16 }}>
            {loading ? "Loading..." : `Load ${broker} Account`}
          </button>
          {unconfiguredBanner}
          {account && (
            <div className="grid-4">
              {Object.entries(account)
                .filter(([k]) => !["broker","balances","can_trade"].includes(k))
                .map(([k, v]) => (
                  <div className="metric-card" key={k}>
                    <div className="metric-label">{k.replace(/_/g," ")}</div>
                    <div className="metric-value" style={{ color: "#00f5d4", fontSize: 18 }}>
                      {typeof v === "number" ? `$${(v as number).toLocaleString()}` : String(v)}
                    </div>
                  </div>
                ))}
              {account.balances && Object.entries(account.balances).slice(0, 8).map(([asset, bal]) => (
                <div className="metric-card" key={asset}>
                  <div className="metric-label">{asset}</div>
                  <div className="metric-value" style={{ color: "#00f5d4", fontSize: 18 }}>{String(bal)}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ─── POSITIONS ─── */}
      {tab === "positions" && (
        <div>
          <button className="btn btn-primary" onClick={loadPositions} disabled={loading} style={{ marginBottom: 16 }}>
            {loading ? "Loading..." : `Load ${broker} Positions`}
          </button>
          {unconfiguredBanner}
          {positions.length > 0 && (
            <div className="card">
              <div className="card-title">Positions ({positions.length})</div>
              <table className="table">
                <thead>
                  <tr>
                    <th>Symbol</th><th>Qty</th><th>Side</th><th>Avg Entry</th>
                    <th>Market Val</th><th>Unrealized P&L</th><th>P&L %</th>
                  </tr>
                </thead>
                <tbody>
                  {positions.map((p: any, i: number) => (
                    <tr key={i}>
                      <td style={{ fontWeight: 700, color: "#00f5d4" }}>{p.symbol}</td>
                      <td>{p.qty}</td>
                      <td><span className={`badge ${p.side === "long" ? "badge-green" : "badge-red"}`}>{p.side}</span></td>
                      <td>${p.avg_entry?.toFixed(2)}</td>
                      <td>${p.market_val?.toFixed(2)}</td>
                      <td style={{ color: p.unrealized_pnl >= 0 ? "#39ff14" : "#ff4060", fontWeight: 700 }}>
                        {p.unrealized_pnl >= 0 ? "+" : ""}${p.unrealized_pnl?.toFixed(2)}
                      </td>
                      <td style={{ color: p.unrealized_pnl_pct >= 0 ? "#39ff14" : "#ff4060" }}>
                        {p.unrealized_pnl_pct ? `${(p.unrealized_pnl_pct * 100).toFixed(2)}%` : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {positions.length === 0 && !loading && !error && (
            <div style={{ color: "#484f58", fontSize: 13 }}>Click Load Positions to fetch from broker.</div>
          )}
        </div>
      )}

      {/* ─── ORDER ─── */}
      {tab === "order" && (
        <div className="grid-2">
          <div className="card">
            <div className="card-title">Order Details</div>
            {OF("Broker", "broker", "text", ["alpaca","binance","binance_futures"])}
            {OF("Symbol", "symbol")}
            {OF("Side", "side", "text", ["buy","sell","long","short"])}
            {OF("Quantity", "qty", "number")}
            {OF("Order Type", "order_type", "text", ["market","limit"])}
            {orderForm.order_type === "limit" && OF("Limit Price ($)", "limit_price", "number")}
            {orderForm.broker === "binance_futures" && <>
              {OF("Leverage", "leverage", "number")}
              {OF("Margin Mode", "margin_mode", "text", ["CROSS","ISOLATED"])}
            </>}
            <div className="alert-warning" style={{ marginBottom: 12, fontSize: 12 }}>
              ⚠ This will place a REAL order if API keys are configured for live trading.
            </div>
            <button className="btn btn-danger" style={{ width: "100%" }} onClick={placeOrder} disabled={loading}>
              {loading ? "Placing..." : "Place Order"}
            </button>
            {unconfiguredBanner}
          </div>
          <div className="card">
            <div className="card-title">Order Result</div>
            {!orderResult && <div style={{ color: "#484f58", fontSize: 13 }}>Fill the form and click Place Order.</div>}
            {orderResult && (
              <div>
                <div className="alert-success" style={{ marginBottom: 12 }}>✓ Order placed successfully</div>
                {Object.entries(orderResult).map(([k, v]) => (
                  <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: "1px solid #1e2d4a22" }}>
                    <span style={{ color: "#8b949e", fontSize: 12 }}>{k}</span>
                    <span style={{ fontWeight: 700 }}>{String(v)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ─── PRICE / ATR ─── */}
      {tab === "price" && (
        <div className="grid-2">
          <div className="card">
            <div className="card-title">Live Price</div>
            <div className="field">
              <label className="label">Symbol</label>
              <input className="input" value={priceSymbol} onChange={e => setPriceSymbol(e.target.value.toUpperCase())} />
            </div>
            <button className="btn btn-primary" style={{ width: "100%" }} onClick={fetchPrice} disabled={loading}>
              {loading ? "Fetching..." : "Get Price"}
            </button>
            {unconfiguredBanner}
            {priceResult && (
              <div style={{ marginTop: 16, textAlign: "center" }}>
                <div style={{ fontSize: 11, color: "#8b949e", marginBottom: 6 }}>{priceResult.broker} — {priceResult.symbol}</div>
                <div style={{ fontSize: 36, fontWeight: 800, color: "#00f5d4" }}>${priceResult.price?.toFixed(4)}</div>
              </div>
            )}
          </div>

          <div className="card">
            <div className="card-title">ATR Calculator</div>
            <div className="field">
              <label className="label">Broker</label>
              <select className="input" value={atrForm.broker} onChange={e => setAtrForm({ ...atrForm, broker: e.target.value as BrokerName })}>
                {BROKERS.map(b => <option key={b.value} value={b.value}>{b.label}</option>)}
              </select>
            </div>
            <div className="field">
              <label className="label">Symbol</label>
              <input className="input" value={atrForm.symbol} onChange={e => setAtrForm({ ...atrForm, symbol: e.target.value.toUpperCase() })} />
            </div>
            <div className="field">
              <label className="label">Timeframe</label>
              <select className="input" value={atrForm.timeframe} onChange={e => setAtrForm({ ...atrForm, timeframe: e.target.value })}>
                {["1m","5m","15m","1h","4h","1d"].map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="field">
              <label className="label">Period</label>
              <input className="input" type="number" value={atrForm.period}
                onChange={e => setAtrForm({ ...atrForm, period: parseInt(e.target.value) || 14 })} />
            </div>
            <button className="btn btn-primary" style={{ width: "100%" }} onClick={fetchAtr} disabled={loading}>
              {loading ? "Calculating..." : "Calculate ATR"}
            </button>
            {atrResult && (
              <div style={{ marginTop: 16, textAlign: "center" }}>
                <div style={{ fontSize: 11, color: "#8b949e", marginBottom: 6 }}>{atrForm.symbol} — {atrForm.timeframe} (period {atrForm.period})</div>
                <div style={{ fontSize: 36, fontWeight: 800, color: "#ffd60a" }}>{atrResult.atr}</div>
                <div style={{ fontSize: 11, color: "#8b949e" }}>ATR Value</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ─── FUTURES CHECKS ─── */}
      {tab === "futures" && (
        <div>
          <button className="btn btn-primary" onClick={loadFutures} disabled={loading} style={{ marginBottom: 16 }}>
            {loading ? "Loading..." : "Check Futures Slots"}
          </button>
          {unconfiguredBanner}
          {futuresInfo && (
            <div className="grid-2">
              {/* Cross mode */}
              <div className="card">
                <div className="card-title">Cross Mode</div>
                <div className={`alert-banner ${futuresInfo.cross.new_cross_trade_allowed ? "alert-success" : "alert-danger"}`}>
                  {futuresInfo.cross.new_cross_trade_allowed ? "✓ Cross trade allowed" : "✗ Cross trade blocked"}
                </div>
                <div style={{ fontSize: 13, color: "#8b949e", marginTop: 8 }}>
                  Active cross positions: {futuresInfo.cross.cross_position_count}
                  <br/>
                  <span style={{ fontSize: 11 }}>Rule: Only 1 cross-mode position at a time.</span>
                </div>
              </div>
              {/* Isolated slots */}
              <div className="card">
                <div className="card-title">Isolated Slots</div>
                <div className={`alert-banner ${futuresInfo.iso.new_trade_allowed ? "alert-success" : "alert-danger"}`}>
                  {futuresInfo.iso.new_trade_allowed ? "✓ Isolated slot available" : "✗ Max isolated slots reached"}
                </div>
                <div style={{ fontSize: 13, color: "#8b949e", marginTop: 8 }}>
                  {futuresInfo.iso.slots_used} / {futuresInfo.iso.slots_used + futuresInfo.iso.slots_remaining} slots used
                </div>
                <div style={{ height: 8, background: "#1c2333", borderRadius: 4, overflow: "hidden", marginTop: 10 }}>
                  <div style={{
                    height: "100%",
                    width: `${futuresInfo.iso.slots_used / (futuresInfo.iso.slots_used + futuresInfo.iso.slots_remaining) * 100}%`,
                    background: futuresInfo.iso.new_trade_allowed ? "#00f5d4" : "#ff4060",
                    borderRadius: 4
                  }} />
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
