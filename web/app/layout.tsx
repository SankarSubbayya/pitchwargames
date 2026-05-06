import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Pitch Wargames - adversarial pitch coach",
  description:
    "Predict the 5 hardest questions a specific investor will ask your specific pitch. 4 composed Apify Actors + Claude Sonnet 4.6.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body>{children}</body>
    </html>
  );
}
