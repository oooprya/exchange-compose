import { RatesList } from "./rates-list";

import styles from "./index.module.css";
import CurrentTime from "../current-time";

export default async function CurrencyRates() {
  return (
    <div className={styles.rates} itemScope itemType="https://schema.org/LocalBusiness">
      <meta itemProp="address" content="Одеса, вул.Успенська, 41" />
                  <meta itemProp="name" content="Обміник №1 Одеса, вул.Успенська, 41" />
                  <meta itemProp="image" content="https://exprivat.com.ua/banner_og.png" />
      <h3 className={styles.title}>
        Курс валют на <CurrentTime />
      </h3>
      <RatesList />
    </div>
  );
}
