import Link from 'next/link'
import { Container } from "@/components/ui/container";
import { RatesList } from "@/components/currency-rates/rates-list-ssr";
import { CardContainer } from '@/components/ui/card-container';
import CurrentTime from "@/components/current-time";
import type { Metadata } from "next";


import styles from "./page.module.css";


export const metadata: Metadata = {
  title: "Обмін валют Одеса — Кращий курс USD, EUR готівкою | EXPRIVAT",
  description:
    "Вигідний курс валют в обмінниках Одеси. USD, EUR, PLN, GBP. Без комісій. Точний курс сьогодні — оновлюється щодня.",
  metadataBase: new URL("https://www.exprivat.com.ua"),
  keywords:"курс доллара в обменниках, курс валюты одесса, курс евро к гривне в обменниках, обменник одесса, доллар в грн в обменниках",

  openGraph: {
    locale: "ua_UA",
    title: "Обмін валют Одеса — Кращий курс USD, EUR готівкою | EXPRIVAT",
    description:
      "Вигідний курс валют в обмінниках Одеси. USD, EUR, PLN, GBP. Без комісій. Точний курс сьогодні — оновлюється щодня.",
    type: "website",
    url: "https://www.exprivat.com.ua/kurs",
    images: {
      url: "kurs.png",
      width: "512px",
      height: "352px",
      alt: "Курс валют в Одесі сьогодні",
    },
    siteName: "exprivat.com.ua",
  },
};

// const jsonLd = {
//   "@context": "https://schema.org",
//   "@type": "WebPage",
//   "name": "Курс валют в Одесе",
//   "description": "Курс обмена валют в Одесе",
//   "mainEntity": {
//       "@type": "ItemList",
//       "itemListElement": [
//             {
//               "@type": "ExchangeRateSpecification",
//               "currency": "USD",
//               "name": "Средний наличный курс",
//               "description": "Курс покупки",
//               "currentExchangeRate": {
//                   "@type": "UnitPriceSpecification",
//                   "price": "-",
//                   "priceCurrency": "UAH"
//               }
//           },
//           {
//               "@type": "ExchangeRateSpecification",
//               "currency": "USD",
//               "name": "Средний наличный курс",
//               "description": "Курс продажи",
//               "currentExchangeRate": {
//                   "@type": "UnitPriceSpecification",
//                   "price": "-",
//                   "priceCurrency": "UAH"
//               }
//           },
//           {
//               "@type": "ExchangeRateSpecification",
//               "currency": "EUR",
//               "name": "Средний наличный курс",
//               "description": "Курс покупки",
//               "currentExchangeRate": {
//                   "@type": "UnitPriceSpecification",
//                   "price": "-",
//                   "priceCurrency": "UAH"
//               }
//           },
//           {
//               "@type": "ExchangeRateSpecification",
//               "currency": "EUR",
//               "name": "Средний наличный курс",
//               "description": "Курс продажи",
//               "currentExchangeRate": {
//                   "@type": "UnitPriceSpecification",
//                   "price": "-",
//                   "priceCurrency": "UAH"
//               }
//           }
//       ]
//   }
// };
{/* <script data-rh="true"
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        /> */}
export default function Kurs() {
  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <Container>
          <div className={styles.inner}>

            <CardContainer>
                <div className={styles.col} itemScope itemType="https://schema.org/WebPage">
                    <RatesList />
                </div>
            </CardContainer>
            <div className={styles.textWrapper}>
              <h1 className={styles.title}>
                Курс валют у обмінниках на <CurrentTime />
              </h1>
                <p className={styles.pageP}>
                  Ми завжди стежимо за актуальним ринковим курсом валют, у нас ви можете обміняти за найвигіднішим курсом
                </p>
                <p className={styles.pageP}>
                  Ми пропонуємо нашим клієнтам найнижчу комісію за купівлю старої валюти, оскільки ми працюємо напряму без посередників.
                </p>
                <p className={styles.pageP}>
                  Завжди в наявності є гривня та валюта, якщо у Вас велика сума на замовлення ми обов&apos;язково вам надамо її
                </p>

            <Link href="/" className={styles.button}>Як забронювати курс?</Link>
            </div>
          </div>
        </Container>
      </section>
    </div>
  )
}