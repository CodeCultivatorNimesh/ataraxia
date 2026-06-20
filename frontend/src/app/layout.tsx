import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "../components/Sidebar";

export const metadata: Metadata = {
  title: "Trading Middleware",
  description: "Behavioral-risk-aware trading middleware bridge",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ display: "flex", minHeight: "100vh" }}>
        <Sidebar />
        <main style={{ marginLeft: 220, flex: 1, minHeight: "100vh", background: "#0d1117" }}>
          <div style={{ padding: "24px", maxWidth: 1300, margin: "0 auto" }}>
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}
