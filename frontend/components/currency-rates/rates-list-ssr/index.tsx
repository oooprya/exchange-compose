import React from "react";
import Link from 'next/link'
import { Rates } from "@/types";

import styles from "./index.module.css";

// function getUniqueByCode<T extends { code: string }>(array: T[]): T[] {
//   return Array.from(new Map(array.map((item) => [item.code, item])).values());
// }

// function sortUrls<T extends { currency: string }>(arr: T[]) {
//   return arr.sort((a, b) => {
//     const numA = parseInt(a.currency.split("/")[4]);
//     const numB = parseInt(b.currency.split("/")[4]);
//     return numA - numB;
//   });
// }

export async function RatesList() {
  const ratesResponse = await fetch(
    `${process.env.NEXT_API_URL}/currencys/?exchanger=1&limit=99`,
    {
      cache: "no-store",
    }
  );
  const { objects: rates }: { objects: Rates[] } =
      await ratesResponse.json();
      // console.log(rates)


  // const rates = sortUrls(getUniqueByCode(ratesList));


  return (
    <>
      {/* Контейнер с информацией об обменнике  */}
      <div className={styles.table} itemScope itemType="https://schema.org/ItemList">
        <div className={styles.tableRow}>
          <span className={`${styles.cell} ${styles.header}`}>Валюта</span>
          <span className={`${styles.cell} ${styles.header}`}>Купівля</span>
          <span className={`${styles.cell} ${styles.header}`}>Продаж</span>
        </div>

        {rates.map((currency) => (
          <React.Fragment key={currency.id}>
             <Link
              className={styles.location}
              href={`/kurs/${currency.code}`}
              prefetch={false}
            >
            <div className={styles.tableRow} itemProp="itemListElement" itemScope itemType="https://schema.org/ExchangeRateSpecification">
                <p className={`${styles.cell} ${styles.tableCell}`} itemProp="name">
                  {currency.code.toLocaleUpperCase()}
                  <span className={`${styles.smal}`}>
                  {currency.currency_name.split(" - ")[1]}
                </span>
                </p>

                <meta itemProp="currency"  content={currency.code} />
                <div className={`${styles.cell} ${styles.tableCell}`} itemProp="currentExchangeRate" itemScope itemType="https://schema.org/UnitPriceSpecification" >
                  <meta itemProp="description" content="Курс покупки"/>
                  <span itemProp="price">{currency.buy}</span>
                  <meta itemProp="priceCurrency" content="UAH"/>
                </div>
                <div className={`${styles.cell} ${styles.tableCell}`} itemProp="currentExchangeRate" itemScope itemType="https://schema.org/UnitPriceSpecification" >
                  <meta itemProp="description" content="Курс продажи"/>
                  <span itemProp="price">{currency.sell}</span>
                  <meta itemProp="priceCurrency" content="UAH"/>
                </div>
            </div>
            </Link>
            {/* <meta itemProp="priceCurrency" content={currency.code.toLocaleUpperCase()} />
            <meta itemProp="url" content={`https://www.exprivat.com.ua/`} /> */}
          </React.Fragment>
        ))}
      </div>
    </>
  );
}
