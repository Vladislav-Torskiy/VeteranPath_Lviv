import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VeteranPath Lviv | Платформа реінтеграції ветеранів",
  description: "Персональна дорожня карта, переклад військового досвіду у резюме, каталог вакансій, грантів та реабілітації для ветеранів на Львівщині.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="uk">
      <body className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
        {children}
      </body>
    </html>
  );
}
