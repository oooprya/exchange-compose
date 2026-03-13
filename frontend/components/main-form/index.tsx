"use client";

import { useEffect, useState } from "react";

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


  const params = useParams<{ code: string }>()


   useEffect(() => {
    const fetchCurrencyList = async () => {
      const response = await fetch("/api/currency?limit=22");
      const { objects } = await response.json() as {objects: Currency[]};
      setCurrencyList(objects);
      if (objects.length > 0) {
        if (!params) {
          setCurrency(objects[0]);
        } else {
          const paramCurr = objects.find(item => {
            // console.log('code', item.code, 'params', params.code)
            return item.code === params.code
          }
          )
          // console.log(objects)
          setCurrency(paramCurr || objects[0] )
          // console.log(params)
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

  // useEffect(() => {
  //   if (currencyList) setCurrency(currencyList[0]);
  // }, [currencyList]);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    let inputValue = event.target.value;

    // Разрешаем только цифры и точку (без минуса)
    inputValue = inputValue.replace(/[^0-9.]/g, "");

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

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    refetch();
  };


const handleInputKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
  if (event.key === "Enter") {
    event.preventDefault(); // Важно, чтобы предотвратить стандартное поведение Enter в форме
    if (!isLoading) { // Добавлена проверка, чтобы не вызывать refetch во время загрузки
      refetch();
    }
  }
};
  return (
    <form
      className={`${styles.form}${
        isSelectOpen ? ` ${styles.selectorOpen}` : ""
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
