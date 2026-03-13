"use client";

import { useEffect } from "react";
import { Rates } from "@/types";
import { useExchangersStore } from "./exchangers-store-provider";

export function RatesProvider({ children }: { children: React.ReactNode }) {
  const setRatesList = useExchangersStore((state) => state.setRatesList);

  const updateRatesList = async () => {
    try {
      const response = await fetch("/api/rates");
      const data = await response.json();
      setRatesList(data as Rates[]);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    updateRatesList();

    const interval = setInterval(() => {
      updateRatesList();
    }, 300000);
    return () => clearInterval(interval);
  });

  return <>{children}</>;
}
