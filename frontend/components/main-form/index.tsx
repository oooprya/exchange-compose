"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useSearchParams } from "next/navigation";

import Select from "@/components/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { FormTabs } from "@/components/main-form/form-tabs";

import { useExchangersStore } from "@/providers";
import { useExchangers } from "@/hooks/useExchangers";
import type { Currency } from "@/types";

import styles from "./index.module.css";
import { useParams } from "next/navigation";

export function MainForm() {
  const [mode, setMode] = useState<"buy" | "sell">("buy");
  const [number, setNumber] = useState<number | "">("");
  const [currencyList, setCurrencyList] = useState<Currency[] | null>(null);
  const [currency, setCurrency] = useState<Currency | null>(null);

  const [isSelectOpen, setIsSelectOpen] = useState<boolean>(false);
  const { setExchangers, setExchangerMode, setAmount, setIsLoading, setError } =
    useExchangersStore((state) => state);


  const { data, refetch, isLoading, isFetching, error } = useExchangers(
    currency,
    number
  );

  const router = useRouter();
  const pathname = usePathname();

  const [autoSearched, setAutoSearched] = useState(false);


  const params = useParams<{ code: string }>()
  const searchParams = useSearchParams();


  useEffect(() => {
    const fetchCurrencyList = async () => {
      const response = await fetch("/api/currency?limit=22");
      const { objects } = await response.json() as { objects: Currency[] };
      setCurrencyList(objects);
      if (objects.length > 0) {
        // Prefer dynamic route param (e.g. /kurs/[code])
        if (params && params.code) {
          const paramCurr = objects.find((item) => item.code === params.code);
          setCurrency(paramCurr || objects[0]);
        } else {
          // If search params present (e.g. ?sell=usdnew&sum=1000), use them
          const sellParam = searchParams?.get("sell");
          const sumParam = searchParams?.get("sum");

          if (sellParam) {
            const found = objects.find((item) => item.code === sellParam);
            if (found) setCurrency(found);
            // set mode to 'sell' when `sell` query param is present
            setMode("sell");
          } else {
            setCurrency(objects[0]);
          }

          if (sumParam) {
            const parsed = parseFloat(sumParam);
            if (!isNaN(parsed)) setNumber(parsed);
          }
        }
      }
    };
    fetchCurrencyList();
  }, []);

  useEffect(() => {
    setExchangers(data ?? undefined);
    setExchangerMode(mode);
    setAmount(typeof number === "number" ? number : "");
    setIsLoading(isLoading || isFetching);
    setError(error);
  }, [
    data,
    mode,
    number,
    isLoading,
    isFetching,
    error,
    setExchangers,
    setExchangerMode,
    setAmount,
    setIsLoading,
    setError,
  ]);

  useEffect(() => {
    if (autoSearched) return;
    const sellParam = searchParams?.get("sell");
    const sumParam = searchParams?.get("sum");
    if ((sellParam || sumParam) && currency) {
      // trigger search once when params present and currency resolved
      refetch();
      setAutoSearched(true);
    }
  }, [currency, number, autoSearched, refetch, searchParams]);

  // useEffect(() => {
  //   if (currencyList) setCurrency(currencyList[0]);
  // }, [currencyList]);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    let inputValue = event.target.value;

    // Разрешаем только цифры и точку (без минуса)
    inputValue = inputValue.replace(/[^0-9.]/g, "");
    console.log('Значение:', inputValue);

    // Предотвращаем ввод нескольких точек подряд
    if ((inputValue.match(/\./g) || []).length > 1) {
      inputValue = inputValue.slice(0, -1);
    }

    if (inputValue === "") {
      setNumber("");
    } else {
      const parsedValue = parseFloat(inputValue);
      if (!isNaN(parsedValue)) {
        setNumber(parsedValue);
      }
    }
  };

  const buildQuery = () => {
    const params = new URLSearchParams();
    if (currency && currency.code) {
      if (mode === "sell") params.set("sell", currency.code);
      else params.set("buy", currency.code);
    }
    if (typeof number === "number" && !Number.isNaN(number)) {
      params.set("sum", String(number));
    }
    return params.toString();
  };

  useEffect(() => {
    if (!pathname) return;
    const query = buildQuery();
    const currentQuery = searchParams?.toString() || "";
    if (query !== currentQuery) {
      router.replace(query ? `${pathname}?${query}` : pathname);
    }
  }, [mode, currency?.code, number, pathname, router, searchParams]);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    // build query params based on mode, currency and amount
    const query = buildQuery();

    // stay on current page and update query string
    router.push(query ? `${pathname}?${query}` : pathname || "/");

    // also trigger existing exchangers fetch
    refetch();
  };


  const handleInputKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      event.preventDefault(); // Важно, чтобы предотвратить стандартное поведение Enter в форме
      if (!isLoading) { // Добавлена проверка, чтобы не вызывать refetch во время загрузки
        // mimic submit behaviour on Enter
        const query = buildQuery();
        router.push(query ? `${pathname}?${query}` : pathname || "/");
        refetch();
      }
    }
  };
  return (
    <form
      className={`${styles.form}${isSelectOpen ? ` ${styles.selectorOpen}` : ""
        }`}
      onSubmit={handleSubmit}
    >
      <FormTabs mode={mode} setMode={setMode} />
      <div className={styles.wrapper}>
        <Select
          options={currencyList}
          value={currency}
          onChange={setCurrency}
          isSelectOpen={isSelectOpen}
          setIsSelectOpen={setIsSelectOpen}
        />
        <Input
          type="text"
          inputMode="numeric"
          pattern="[0-9]*"
          value={number}
          onChange={handleChange}
          onKeyDown={handleInputKeyDown}
          placeholder="Введіть суму"
        />
        <span className={styles.infoText}>⚠️ На купюри номіналом 1, 2, 5, 10, 20, 50 $ оптовий курс не діє»</span>
        <Button disabled={isLoading} >Знайти де обміняти</Button>
      </div>
    </form>
  );
}
