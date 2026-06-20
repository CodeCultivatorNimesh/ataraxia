"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/dashboard",  label: "Dashboard",    icon: "⬛" },
  { href: "/position",   label: "Position Size", icon: "📐" },
  { href: "/risk",       label: "Risk Engine",   icon: "🛡" },
  { href: "/patterns",   label: "Patterns",      icon: "🕯" },
  { href: "/journal",    label: "Journal",       icon: "📒" },
  { href: "/behavioral", label: "Behavioral",    icon: "🧠" },
  { href: "/broker",     label: "Broker",        icon: "🔌" },
  { href: "/analytics",  label: "Analytics",     icon: "📊" },
];

export default function Sidebar() {
  const path = usePathname();
  return (
    <aside style={{
      width: 220,
      minHeight: "100vh",
      background: "#0b0f1a",
      borderRight: "1px solid #1e2d4a",
      display: "flex",
      flexDirection: "column",
      position: "fixed",
      top: 0,
      left: 0,
      zIndex: 100,
    }}>
      {/* Logo */}
      <div style={{ padding: "20px 20px 16px", borderBottom: "1px solid #1e2d4a" }}>
        <div style={{ fontSize: 13, fontWeight: 800, color: "#00f5d4", letterSpacing: "0.12em", textTransform: "uppercase" }}>
          Trading
        </div>
        <div style={{ fontSize: 10, color: "#484f58", letterSpacing: "0.15em", textTransform: "uppercase", marginTop: 2 }}>
          Middleware v1.0
        </div>
      </div>

      {/* Nav items */}
      <nav style={{ flex: 1, padding: "12px 8px" }}>
        {NAV.map(({ href, label, icon }) => {
          const active = path.startsWith(href);
          return (
            <Link key={href} href={href} style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              padding: "9px 12px",
              borderRadius: 8,
              marginBottom: 2,
              textDecoration: "none",
              fontSize: 13,
              fontWeight: active ? 700 : 500,
              color: active ? "#00f5d4" : "#8b949e",
              background: active ? "rgba(0,245,212,0.08)" : "transparent",
              transition: "all 0.15s",
            }}>
              <span style={{ fontSize: 15 }}>{icon}</span>
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div style={{ padding: "12px 20px", borderTop: "1px solid #1e2d4a", fontSize: 10, color: "#484f58" }}>
        FastAPI + Next.js
      </div>
    </aside>
  );
}
