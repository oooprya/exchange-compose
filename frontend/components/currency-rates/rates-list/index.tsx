"use client";

import React, { useState } from "react";

import styles from "./index.module.css";
import { useExchangersStore } from "@/providers";
import { Spinner } from "@/components/ui/spinner";
import Link from "next/link";

function getUniqueByCode<T extends { code: string }>(array: T[]): T[] {
  return Array.from(new Map(array.map((item) => [item.code, item])).values());
}

function sortUrls<T extends { currency: string }>(arr: T[]) {
  return arr.sort((a, b) => {
    const numA = parseInt(a.currency.split("/")[4]);
    const numB = parseInt(b.currency.split("/")[4]);
    return numA - numB;
  });
}

export function RatesList() {
  const [visibleCount] = useState(4);
  // const [visibleCount, setVisibleCount] = useState(5);
  const ratesList = useExchangersStore((store) => store.ratesList);

  if (!ratesList) {
    return <Spinner variant="accent" />;
  }

  const rates = sortUrls(getUniqueByCode(ratesList));
  // const isAllVisible = rates && visibleCount >= rates.length;

  return (
    <>
      {/* Контейнер с информацией об обменнике  */}
      <div className={styles.table} itemScope itemType="https://schema.org/Offer">

        <span className={`${styles.cell} ${styles.header}`}>Валюта</span>
        <span className={`${styles.cell} ${styles.header}`}>Купівля</span>
        <span className={`${styles.cell} ${styles.header}`}>Продаж</span>

        {rates.slice(0, visibleCount).map((currency) => (
          <React.Fragment key={currency.id}>

            <span className={`${styles.cell} ${styles.tableCell}`} itemProp="name">
              {currency.code.toLocaleUpperCase()}
            </span>
            <span className={`${styles.cell} ${styles.tableCell}`} itemProp="price">
              {currency.buy}
            </span>
            <span className={`${styles.cell} ${styles.tableCell}`} itemProp="price">
              {currency.sell}
            </span>

            {/* <meta itemProp="priceCurrency" content={currency.code.toLocaleUpperCase()} />
            <meta itemProp="url" content={`https://www.exprivat.com.ua/`} /> */}
          </React.Fragment>
        ))}
      </div>
      {/* {!isAllVisible && (
        <button
          className={styles.button}
          onClick={() => setVisibleCount(rates.length)}
        >
          Курс всіх валют
        </button>
      )} */}
      <Link  href="/kurs" title="Курс валют" className={styles.button}>
          <span>Курс всіх валют</span>
      </Link>
    </>
  );
}
