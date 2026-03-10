import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "UNO — The Card Game",
  description: "Play UNO online against AI opponents. Neon-themed browser card game built with Next.js.",
  icons: {
    icon: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
