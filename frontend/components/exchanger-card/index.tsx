"use client";

import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Location } from "@/components/ui/icons";
import { useExchangersStore } from "@/providers";
import type { Exchanger, OrderData } from "@/types";

import styles from "./index.module.css";

type ExchangerCardProps = {
  exchanger: Exchanger;
  mode: "buy" | "sell";
};

export function ExchangerCard({ exchanger, mode }: ExchangerCardProps) {
  const value = mode === "buy" ? exchanger.buy : exchanger.sell;
  const amount = useExchangersStore((state) => state.amount);
  const setOrderData = useExchangersStore((state) => state.setOrderData);
  const setIsOrderOpen = useExchangersStore((state) => state.setOrderBarOpen);

  const handleBook = () => {
    const orderData: OrderData = {
      address: exchanger.address,
      addressMap: exchanger.address_map,
      currencyName: exchanger.currency_name,
      price: exchanger[mode],
      hours: exchanger.working_hours,
      amount,
      mode,
    };

    setOrderData(orderData);
    setIsOrderOpen(true);
  };

  return (
    <article className={styles.card}>
      <div className={styles.content}>
        <div className={styles.info}>
          <span className={styles.rate}>{value}</span>
          <span className={styles.address}>{exchanger.address}</span>
        </div>
        <Link
          className={styles.location}
          href={exchanger.address_map}
          target="_blank"
        >
          <div className={styles.iconWrapper}>
            <Location className={styles.icon} />
          </div>
          <span className={styles.locationText}>Маршрут</span>
        </Link>
      </div>

      <Button size="small" onClick={handleBook}>
        Забронювати
      </Button>
    </article>
  );
}
