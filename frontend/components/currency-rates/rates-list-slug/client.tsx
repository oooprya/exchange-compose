"use client";
import Link from 'next/link'
import React, { useState, useRef, useEffect } from "react";
import { Rates } from "@/types";
import styles from "./index.module.css";

function getUniqueByCode<T extends { code: string }>(array: T[]): T[] {
  return Array.from(new Map(array.map((item) => [item.code, item])).values());
}

function sortRates<T extends { id: number }>(arr: T[]) {
  return arr.sort((a, b) => a.id - b.id);
}

export default function ClientRatesList({ rates }: { rates: Rates[] }) {
  const [expanded, setExpanded] = useState(false);

  const contentRef = useRef<HTMLDivElement>(null);
  const [height, setHeight] = useState("0px");

  const unique = sortRates(getUniqueByCode(rates));

  useEffect(() => {
    if (contentRef.current) {
      setHeight(expanded ? `${contentRef.current.scrollHeight}px` : "0px");
    }
  }, [expanded, unique]);

  const shortList = unique.slice(0, 5);

  return (
    <>
      <div className={styles.table}>
        <div className={styles.tableRow}>
          <span className={`${styles.cell} ${styles.header}`}>Валюта</span>
          <span className={`${styles.cell} ${styles.header}`}>Купівля</span>
          <span className={`${styles.cell} ${styles.header}`}>Продаж</span>
        </div>

        {shortList.map((currency) => (
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
          </React.Fragment>
        ))}

      </div>

      {/* скрытый блок */}
      <div
        ref={contentRef}
        className={styles.expandWrapper}
        style={{ maxHeight: height }}
      >
        {unique.slice(5).map((currency) => (
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
          </React.Fragment>
        ))}
      </div>

      {unique.length > 5 && (
        <button
          className={styles.button}
          onClick={() => setExpanded((p) => !p)}
        >
          {expanded ? "Сховати" : "Курс всіх валют"}
        </button>
      )}
    </>
  );
}
