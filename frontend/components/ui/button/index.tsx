import styles from "./index.module.css";

type ButtonProps = {
  variant?: "default" | "ghost";
  size?: "small" | "default";
} & React.ButtonHTMLAttributes<HTMLButtonElement> &
  React.PropsWithChildren;

export function Button({
  children,
  variant = "default",
  size = "default",
  ...otherProps
}: ButtonProps) {
  return (
    <button
      className={`${styles.btn}
      ${variant === "default" ? ` ${styles.default}` : ` ${styles.ghost}`}
      ${size === "small" ? ` ${styles.btnSmall}` : ""}`}
      {...otherProps}
    >
      {children}
    </button>
  );
}
