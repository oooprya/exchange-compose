import Link from "next/link";

import { Location } from "@/components/ui/icons";

import styles from "./index.module.css";
import { ExchangersListItem } from "@/types";

export default async function ExchangersList() {
  const exchangersResponse = await fetch(
    `${process.env.NEXT_API_URL}/exchangers/`,
    {
      cache: "no-store",
    }
  );
  const { objects: exchangers }: { objects: ExchangersListItem[] } =
    await exchangersResponse.json();

  return (
    <div className={styles.exchangers}>
      <h3 className={styles.title}>обмінні пункти</h3>
      <div className={styles.list}>
        {exchangers.map((exchanger) => (
          <div className={styles.exchanger} key={`exchanger-${exchanger.id}`}>
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
            <Link
              className={styles.location}
              href={`/obmen/${exchanger.slug}`}
            >
            <div className={styles.info}>
              <span className={styles.address}>{exchanger.address}</span>
              <span className={styles.hours}>{exchanger.working_hours}</span>
            </div>
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
