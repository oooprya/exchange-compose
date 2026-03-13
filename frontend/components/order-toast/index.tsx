"use client";

import Link from "next/link";
import { Roboto } from "next/font/google";
import { AnimatePresence, motion } from "framer-motion";

import { Close } from "@/components/ui/icons";
import { Location } from "@/components/ui/icons";
import { Hours } from "@/components/hours";

import { useExchangersStore } from "@/providers";
import { isNowInTimeRange } from "@/utils";
import { useDisableBodyScroll } from "@/hooks/useDisableBodyScroll";

import styles from "./index.module.css";

const sidebarVariants = {
  hidden: { x: "100%" },
  visible: { x: 0 },
  exit: { x: "100%" },
};

const roboto = Roboto({
  weight: ["400", "700"],
  subsets: ["cyrillic"],
});

export default function OrderToast() {
  const isToastOpen = useExchangersStore((store) => store.isOrderToastOpen);
  const setToastOpen = useExchangersStore((store) => store.setToastOpen);
  const responseData = useExchangersStore((store) => store.orderResponse);
  const orderData = useExchangersStore((store) => store.orderData);

  useDisableBodyScroll(isToastOpen);

  const handleClose = () => {
    setToastOpen(false);
    window.location.reload();
  };

  if (!responseData || !orderData) return null;

  const hours = isNowInTimeRange(orderData.hours);

  return (
    <AnimatePresence>
      {isToastOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className={styles.overlay}
            onClick={handleClose}
          />
          <motion.aside
            initial="hidden"
            animate={isToastOpen ? "visible" : "hidden"}
            exit="exit"
            variants={sidebarVariants}
            transition={{ type: "tween", duration: 0.3 }}
            className={styles.sidebar}
          >
            <button onClick={handleClose} className={styles.close}>
              <Close />
            </button>
            <div className={styles.content}>
              <h2 className={`${styles.title} ${roboto.className}`}>
                Дякуємо!
                <br />
                Бронювання відправлено
              </h2>

              <div className={styles.orderNumber}>
                <h4 className={styles.orderNumberTitle}>№ Бронювання</h4>
                <span className={`${styles.value} ${roboto.className}`}>
                  {responseData.id.toString().padStart(4, "0")}
                </span>
                <div className={styles.warning}>
                  <span className={styles.warningIcon}>!</span>
                  <p className={styles.warningText}>
                    Зробіть скріншот та запам&apos;ятайте номер броні
                  </p>
                </div>
              </div>

              <div className={styles.info}>
                {/* LOCATION */}
                <div className={styles.locationWrapper}>
                  <div className={styles.locationInfo}>
                    <div className={styles.address}>
                      {responseData?.address_exchanger}
                    </div>
                    <Hours hours={hours} />
                  </div>
                  <Link
                    className={styles.location}
                    href={orderData.addressMap}
                    target="_blank"
                  >
                    <div className={styles.iconWrapper}>
                      <Location className={styles.icon} />
                    </div>
                    <span className={styles.locationText}>Маршрут</span>
                  </Link>
                </div>

                {/* CURRENCY */}
                <div className={styles.currency}>
                  <div className={styles.currencyName}>
                    {orderData.currencyName}
                  </div>
                  <div className={styles.currencyValue}>{orderData.amount}</div>
                </div>

                {/* CONCLUSION */}
                <div className={styles.conclusion}>
                  <div className={styles.conclusionText}>
                    {orderData.mode === "buy" ? "Вы отримуйте" : "Ви віддаєте"}
                  </div>
                  <div className={styles.conclusionValue}>
                    {(
                      Number(orderData.amount) * Number(orderData.price)
                    ).toLocaleString("ua-UA")}
                  </div>
                </div>
              </div>
                    <p className={styles.infoPrivateBot}>Для перевірки статусу бронювання курсу перейдіть в телеграм бот</p>
                <Link
                    className={styles.linkPrivateBot}
                    href='https://t.me/private_exchange_od_bot'
                    target="_blank"
                  >
                    Перевірити статус
                  </Link>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
