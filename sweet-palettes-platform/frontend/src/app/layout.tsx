import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Sweet Palettes | Sweet Moments Start Here",
  description: "AI-powered dessert business platform with ordering, booking, CRM, and analytics."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
