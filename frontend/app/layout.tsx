import type { Metadata } from "next";
// remove next/font imports to avoid turbopack issues
import "./globals.css";

// fonts will be loaded via css @import in globals.css

// keep variables for font families if needed
const geistSans = {
  variable: "--font-geist-sans",
};

const geistMono = {
  variable: "--font-geist-mono",
};

export const metadata: Metadata = {
  title: "Остаточные знания",
  description: "Сервис для согласования дат сдачи отчетов и получения отчетов по остаточным знаниям",
  icons: {
    icon: [{ url: "/csh/favicon.svg?v=2", type: "image/svg+xml" }],
    shortcut: [{ url: "/csh/favicon.svg?v=2", type: "image/svg+xml" }],
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <head>
        <link rel="icon" href="/csh/favicon.svg?v=2" type="image/svg+xml" />
        <link rel="shortcut icon" href="/csh/favicon.svg?v=2" type="image/svg+xml" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
