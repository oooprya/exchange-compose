import styles from "./index.module.css";

type ButtonProps = React.HTMLAttributes<HTMLDivElement> &
  React.PropsWithChildren;

export function Container({ children, ...otherProps }: ButtonProps) {
  return (
    <div className={styles.container} {...otherProps}>
      {children}
    </div>
  );
}
