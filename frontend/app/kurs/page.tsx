import Link from 'next/link'
import { Container } from "@/components/ui/container";
import { RatesList } from "@/components/currency-rates/rates-list-ssr";
import { CardContainer } from '@/components/ui/card-container';
import CurrentTime from "@/components/current-time";
import type { Metadata } from "next";


import styles from "./page.module.css";


export const metadata: Metadata = {
  title: "Курс валют в Одесі сьогодні — USD, EUR та інші | EXPRIVAT",
  description:
    "Актуальний курс долара, євро та інших валют в обмінниках Одеси. Курс купівлі та продажу USD, EUR, PLN, GBP. Оберіть зручний обмінний пункт та забронюйте курс онлайн.",
  metadataBase: new URL("https://exprivat.com.ua"),
  alternates: {
    canonical: `/kurs`,
  },
  keywords: [
  "курс валют Одеса",
  "курс долара Одеса",
  "курс євро Одеса",
  "курс валют в обмінниках Одеси",
  "курс долара в обмінниках",
  "курс євро в обмінниках",
  "обмін валют Одеса",
],

  openGraph: {
    locale: "ua_UA",
    title: "Курс валют в Одесі сьогодні — USD, EUR та інші | EXPRIVAT",
    description:
      "Актуальний курс долара, євро та інших валют в обмінниках Одеси. Курс купівлі та продажу USD, EUR, PLN, GBP. Оберіть зручний обмінний пункт та забронюйте курс онлайн.",
    type: "website",
    url: "https://exprivat.com.ua/kurs",
    images: {
      url: "kurs.png",
      width: "512px",
      height: "352px",
      alt: "Курс валют в Одесі сьогодні",
    },
    siteName: "EXPRIVAT",
  },
};


const jsonLd = {
  "@context": "https://schema.org",
  "@type": "WebPage",
  name: "Курс валют в обмінниках Одеси",
  description:
    "Актуальний курс долара, євро та інших валют в обмінниках Одеси.",
  url: "https://exprivat.com.ua/kurs",
  inLanguage: "uk-UA",
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
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLd),
        }}
      />
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
                 Курс валют в обмінниках Одеси
              </h1>
              <p className={styles.updated}>
                Актуальний курс на <CurrentTime />
              </p>

              <p className={styles.pageP}>
                Ми щодня оновлюємо курс валют у наших обмінних
                пунктах Одеси. Переглядайте актуальний курс купівлі
                та продажу долара, євро та інших іноземних валют.
              </p>

              <p className={styles.pageP}>
                Оберіть зручний для вас обмінний пункт та уточніть
                актуальний курс перед здійсненням операції.
              </p>
              <p className={styles.pageP}>
                Потрібен обмін великої суми? Ви можете заздалегідь
                забронювати валюту та уточнити індивідуальні умови.
              </p>

            <Link href="/" className={styles.button}>Як забронювати курс?</Link>
            </div>
          </div>
        </Container>
      </section>
      <section className={styles.textWrapper}>
        <Container>
          <div className={styles.inner}>
            <h2 className={styles.stepsTitle}>Курс валют в обмінниках Одеси</h2>

            <p className={styles.pageP}>
              На цій сторінці ви можете переглянути актуальний курс
              долара, євро та інших іноземних валют у наших обмінних
              пунктах Одеси.
            </p>

            <h2 className={styles.stepsTitle}>Курс долара та євро в Одесі</h2>

            <p className={styles.pageP}>
              У таблиці ви знайдете курс купівлі та продажу USD,
              EUR, GBP, CHF, PLN та інших валют.
            </p>

            <p className={styles.pageP}>
              Потрібно обміняти старі або пошкоджені купюри?{" "}
              <Link href="/pryiom-poshkodzhenykh-kupyur">
                Дізнайтесь про прийом зношених купюр
              </Link>.
            </p>
          </div>
        </Container>
      </section>
    </div>
  )
}