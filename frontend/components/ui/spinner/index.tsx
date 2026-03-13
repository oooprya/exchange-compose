import styles from "./index.module.css";

type SpinnerProps = {
  variant?: "default" | "accent" | "button";
};

export function Spinner({ variant = "default" }: SpinnerProps) {
  return (
    <span
      className={`${styles.spinner}${
        variant === "accent" ? ` ${styles.accent}` : ""
      }${variant === "button" ? ` ${styles.button}` : ""}`}
    ></span>
  );
}
