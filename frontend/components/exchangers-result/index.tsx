"use client";

import { Container } from "@/components/ui/container";
import { ExchangerCard } from "@/components/exchanger-card";
import { Spinner } from "@/components/ui/spinner";
import { useExchangersStore } from "@/providers";

import styles from "./index.module.css";

export default function ExchangersResult() {
  const { data, exchangerMode, isLoading, error } = useExchangersStore(
    (state) => state
  );

  if (isLoading) {
    return <Spinner variant="accent" />;
  }
  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <section className={styles.result}>
      <Container>
        <ul className={styles.list}>
          {data?.objects.map((item) => (
            <li className={styles.item} key={item.id}>
              <ExchangerCard exchanger={item} mode={exchangerMode} />
            </li>
          ))}
        </ul>
      </Container>
    </section>
  );
}
