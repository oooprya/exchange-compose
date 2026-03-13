"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";

import { BackArrow } from "@/components/ui/icons";
import { Location } from "@/components/ui/icons";
import { Button } from "@/components/ui/button";
import { PhoneInput } from "@/components/phone-input";
import { Hours } from "@/components/hours";

import { useCreateOrder } from "@/hooks/useCreateOrder";
import { useDisableBodyScroll } from "@/hooks/useDisableBodyScroll";
import { useExchangersStore } from "@/providers";
import { isNowInTimeRange } from "@/utils";
import { OrderData } from "@/types";

import styles from "./index.module.css";

const MODE_DICTIONARY = {
  sell: "продаж",
  buy: "купівля",
};

const sidebarVariants = {
  hidden: { x: "100%" },
  visible: { x: 0 },
  exit: { x: "100%" },
};

export function OrderBar() {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [errorPhone, setErrorPhone] = useState(false);
  const { mutate, isPending, error } = useCreateOrder();
  const orderData = useExchangersStore((store) => store.orderData);
  const isOpen = useExchangersStore((store) => store.isOrderBarOpen);
  const setIsOpen = useExchangersStore((store) => store.setOrderBarOpen);

  useDisableBodyScroll(isOpen);

  const handleClose = () => setIsOpen(false);

  const onChange = (value: string) => {
    setErrorPhone(false);
    setPhoneNumber(value);
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>, data: OrderData) => {
    e.preventDefault();

    if (!phoneNumber || phoneNumber.length < 12) {
      setErrorPhone(true);
      return;
    }

    const orderPostData = {
      address_exchanger: data.address,
      buy_or_sell: MODE_DICTIONARY[data.mode],
      currency_name: data.currencyName,
      exchange_rate: data.price,
      order_sum: typeof data.amount === "number" ? data.amount : 0,
      clients_telephone: `+${phoneNumber}`,
    };

    mutate(orderPostData);
  };

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [setIsOpen]);

  if (!orderData) return null;

  const hours = isNowInTimeRange(orderData.hours);

  return (
    <AnimatePresence>
      {isOpen && (
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
            animate={isOpen ? "visible" : "hidden"}
            exit="exit"
            variants={sidebarVariants}
            transition={{ type: "tween", duration: 0.3 }}
            className={styles.sidebar}
          >
            <button className={styles.backButton} onClick={handleClose}>
              <BackArrow />
            </button>
            {error && <div className={styles.error}>{error.message}</div>}
            <h2 className={styles.title}>Бронювання</h2>

            <form
              className={styles.form}
              onSubmit={(e) => handleSubmit(e, orderData)}
            >
              {/* PHONE INPUT */}
              <PhoneInput
                value={phoneNumber}
                onChange={onChange}
                error={errorPhone}
              />

              {/* INFO */}
              <div className={styles.info}>
                <div className={styles.infoText}>
                  <h4 className={styles.infoTitle}>Отримання: </h4>
                  <p className={styles.infoDescription}>
                    самовивіз з обмінному відділенні
                  </p>
                </div>
                <div className={styles.infoText}>
                  <h4 className={styles.infoTitle}>Оплата: </h4>
                  <p className={styles.infoDescription}>
                    безпосередньо в обмінному відділенні
                  </p>
                </div>
                <div className={styles.infoText}>
                  <h4 className={styles.infoTitle}>Термін броні: </h4>
                  <p className={styles.infoDescription}>протягом 1 години</p>
                </div>
              </div>

              {/* LOCATION */}
              <div className={styles.locationWrapper}>
                <div className={styles.locationInfo}>
                  <div className={styles.address}>{orderData.address}</div>
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

              <Button disabled={!hours.isNow || isPending} type="submit">
                {hours.isNow
                  ? "підтвердити бронювання"
                  : `Повертайтеся з ${hours.start} до ${hours.end}`}
              </Button>
            </form>
          </motion.aside>
        </>
      )}
      )
    </AnimatePresence>
  );
}
