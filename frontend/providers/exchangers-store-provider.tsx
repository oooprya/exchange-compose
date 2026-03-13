"use client";

import { type ReactNode, createContext, useRef, useContext } from "react";
import { useStore } from "zustand";
import { type ExchangersStore, createExchangersStore } from "@/store";

export type ExchangersStoreApi = ReturnType<typeof createExchangersStore>;

export const ExchangersStoreContext = createContext<
  ExchangersStoreApi | undefined
>(undefined);

export interface ExchangersStoreProviderProps {
  children: ReactNode;
}

export const ExchangersStoreProvider = ({
  children,
}: ExchangersStoreProviderProps) => {
  const storeRef = useRef<ExchangersStoreApi>(null);
  if (!storeRef.current) {
    storeRef.current = createExchangersStore();
  }

  return (
    <ExchangersStoreContext.Provider value={storeRef.current}>
      {children}
    </ExchangersStoreContext.Provider>
  );
};

export const useExchangersStore = <T,>(
  selector: (store: ExchangersStore) => T
): T => {
  const exchangersStoreContext = useContext(ExchangersStoreContext);

  if (!exchangersStoreContext) {
    throw new Error(
      `useExchangersStore must be used within ExchangersStoreProvider`
    );
  }

  return useStore(exchangersStoreContext, selector);
};
