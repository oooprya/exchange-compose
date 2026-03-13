import React from "react";
import { Rates } from "@/types";
import ClientRatesList from "./client";




export async function RatesList({ exchangerId }: { exchangerId: number }) {
  const ratesResponse = await fetch(
    `${process.env.NEXT_API_URL}/currencys/?exchanger=${exchangerId}&limit=99`,
    {
      cache: "no-store",
    }
  );
  const { objects: rates }: { objects: Rates[] } = await ratesResponse.json();

  if (!rates || !rates.length) {
    return <div>Курсів немає</div>;
  }

  return <ClientRatesList rates={rates} />;

  // return (
  //   <>
  //     {/* Контейнер с информацией об обменнике  */}
  //     <div className={styles.table} itemScope itemType="https://schema.org/ItemList">
  //       <div className={styles.tableRow}>
  //         <span className={`${styles.cell} ${styles.header}`}>Валюта</span>
  //         <span className={`${styles.cell} ${styles.header}`}>Купівля</span>
  //         <span className={`${styles.cell} ${styles.header}`}>Продаж</span>
  //       </div>

  //       {rates.map((currency) => (
  //         <React.Fragment key={currency.id}>
  //           <div className={styles.tableRow} itemProp="itemListElement" itemScope itemType="https://schema.org/ExchangeRateSpecification">
  //               <p className={`${styles.cell} ${styles.tableCell}`} itemProp="name">
  //                 {currency.code.toLocaleUpperCase()}
  //                 <span className={`${styles.smal}`}>
  //                 {currency.currency_name.split(" - ")[1]}
  //               </span>
  //               </p>

  //               <meta itemProp="currency"  content={currency.code} />
  //               <div className={`${styles.cell} ${styles.tableCell}`} itemProp="currentExchangeRate" itemScope itemType="https://schema.org/UnitPriceSpecification" >
  //                 <meta itemProp="description" content="Курс покупки"/>
  //                 <span itemProp="price">{currency.buy}</span>
  //                 <meta itemProp="priceCurrency" content="UAH"/>
  //               </div>
  //               <div className={`${styles.cell} ${styles.tableCell}`} itemProp="currentExchangeRate" itemScope itemType="https://schema.org/UnitPriceSpecification" >
  //                 <meta itemProp="description" content="Курс продажи"/>
  //                 <span itemProp="price">{currency.sell}</span>
  //                 <meta itemProp="priceCurrency" content="UAH"/>
  //               </div>
  //           </div>
  //         </React.Fragment>
  //       ))}
  //     </div>
  //   </>
  // );
}
