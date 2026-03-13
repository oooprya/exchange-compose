import styles from "./index.module.css";

type CardContainerProps = React.HTMLAttributes<HTMLDivElement> &
  React.PropsWithChildren;

export function CardContainer({ children, ...otherProps }: CardContainerProps) {
  return (
    <div className={styles.Card} {...otherProps}>
      {children}
    </div>
  );
}
