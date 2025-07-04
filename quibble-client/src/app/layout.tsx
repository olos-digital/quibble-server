import type { Metadata } from "next";
import localFont from 'next/font/local'
import './globals.css'

const rollbox = localFont({
  src: [
    {
      path: '../../public/assets/fonts/Rollbox/RollboxRegular.ttf',
      weight: '400',
      style: 'normal',
    },
    {
      path: '../../public/assets/fonts/Rollbox/RollboxBold.ttf',
      weight: '700',
      style: 'normal',
    },
  ],
  variable: '--font-rollbox',
  display: 'swap',
})

export const metadata: Metadata = {
  title: "Quibble AI",
  description: "AI Assistant to automate the social media posting process",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={rollbox.variable}>
      <body className="font-rollbox antialiased">
        {children}
      </body>
    </html>
  );
}
