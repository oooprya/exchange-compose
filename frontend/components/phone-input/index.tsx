import { useRef } from "react";
import { IMaskInput } from "react-imask";

import styles from "./index.module.css";

type PhoneNumberProps = {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  error: boolean;
};

const getInputColor = (value: string) => {
  if (!value || value.length < 6) return "attention";
  if (value.length < 12) return "warning";
  return "";
};

export function PhoneInput({
  value,
  onChange,
  placeholder = "+380",
  error,
}: PhoneNumberProps) {
  const ref = useRef(null);
  const inputRef = useRef(null);

  return (
    <div className={styles.formControl}>
      <label className={styles.label} htmlFor="phone">
        Телефон
      </label>

      <IMaskInput
        id="phone"
        type="tel"
        name="phone"
        mask={"+{38} (000) 000-00-00"}
        radix="."
        value={value}
        unmask={true}
        ref={ref}
        inputRef={inputRef}
        onAccept={(_, mask) => {
          let unmasked = mask.unmaskedValue;
          if (!unmasked.startsWith("380")) {
            unmasked = "380" + unmasked.slice(2);
          }
          onChange(unmasked);
        }}
        placeholder={placeholder}
        className={`${styles.input} ${styles[getInputColor(value)]}`}
      />
      {error && (
        <span className={styles.errorText}>невірно введений номер</span>
      )}
    </div>
  );
}
