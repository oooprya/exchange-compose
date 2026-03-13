import { useMutation } from "@tanstack/react-query";

import { createOrder } from "@/utils/api";
import { useExchangersStore } from "@/providers";

export function useCreateOrder() {
  const setOrderBarIsOpen = useExchangersStore(
    (store) => store.setOrderBarOpen
  );
  const setToastBarIsOpen = useExchangersStore((store) => store.setToastOpen);
  const setOrderResponse = useExchangersStore(
    (store) => store.setOrderResponse
  );

  return useMutation({
    mutationFn: createOrder,
    onSuccess: (data) => {
      setOrderBarIsOpen(false);
      setOrderResponse(data);
      setToastBarIsOpen(true);
    },
  });
}
