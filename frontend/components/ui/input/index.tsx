import styles from './index.module.css';

export function Input({
  ...otherProps
}: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input className={styles.input} {...otherProps} />;
}
