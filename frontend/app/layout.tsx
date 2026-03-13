import localFont from "next/font/local";
import Script from "next/script";
import type { Metadata } from "next";
import { Header } from "@/components/header";
import { Contacts } from "@/components/contacts";
import { Footer } from "@/components/footer";

import { OrderBar } from "@/components/order-bar";
import OrderToast from "@/components/order-toast";
import PageDecor from "@/components/page-decor";

import { QueryProvider, ExchangersStoreProvider } from "@/providers";
import { RatesProvider } from "@/providers/rates-provider";


import "@/styles/normalize.css";
import "@/styles/globals.css";



const eUkraine = localFont({
  src: [
    {
      path: "./fonts/e-ukraine-light.woff2",
      weight: "300",
      style: "normal",
    },
    {
      path: "./fonts/e-ukraine-regular.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "./fonts/e-ukraine-bold.woff2",
      weight: "700",
      style: "normal",
    },
  ],
});

export const metadata: Metadata = {
  title: "Курс долара в Одесі сьогодні – актуальні обмінники та найкращий курс валют",
  description:
    "Шукаєте, де вигідно обміняти валюту в Одесі? Актуальний курс долара, євро та інших валют у наших обмінних пунктах. Оновлення щодня!",
  metadataBase: new URL("https://www.exprivat.com.ua/"),
  keywords:"курс долара Одеса, обмін валют Одеса, актуальний курс обміну, обмінники Одеса, курс євро до гривні",

  openGraph: {
    locale: "ua_UA",
    title: "Просто і вигідно обміняти валюту",
    description:
      "Шукаєте, де вигідно обміняти валюту в Одесі? Актуальний курс долара, євро та інших валют у наших обмінних пунктах. Оновлення щодня!",
    type: "website",
    url: "https://www.exprivat.com.ua/",
    images: {
      url: "/banner_og.png",
      width: "512px",
      height: "512px",
      alt: "Найкращий курс валют в Одесі сьогодні",
    },
    siteName: "exprivat.com.ua",
  },
};
const GTM_ID = "GTM-NJVCGC6K"; // Ваш GTM ID



export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* GTM Script */}
      <Script
        id="gtm-script"
        strategy="afterInteractive"
        dangerouslySetInnerHTML={{
          __html: `
            (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
            new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
            j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
            'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
            })(window,document,'script','dataLayer','${GTM_ID}');
          `,
        }}
      />
        {/* <Script
          id="google-analytics"
          strategy="afterInteractive"
          dangerouslySetInnerHTML={{
            __html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', 'G-STJ7PH7DVD');
            `,
          }}
        /> */}
        <meta name="apple-mobile-web-app-title" content="exprivat" />

      </head>
      <body className={`${eUkraine.className}`}>
        {/* Google Tag Manager (noscript) */}

        <noscript
          dangerouslySetInnerHTML={{
            __html: `
              <iframe src="https://www.googletagmanager.com/ns.html?id=${GTM_ID}"
              height="0" width="0" style="display:none;visibility:hidden"></iframe>
            `,
          }}
        />
        <QueryProvider>
          <ExchangersStoreProvider>
            <RatesProvider>
              <Header />
              <main>{children}</main>
              <Contacts />
              <Footer />
              <OrderBar />
              <OrderToast />
            </RatesProvider>
          </ExchangersStoreProvider>
        </QueryProvider>
        <PageDecor />
      </body>
    </html>
  );
}
