import styles from "./index.module.css";

export function Hours({
  hours,
}: {
  hours: {
    isNow: boolean;
    start: string;
    end: string;
  };
}) {
  if (hours.isNow) {
    return <div className={styles.hours}>Відчинено до {hours.end}</div>;
  }

  return (
    <div className={styles.hours}>
      <span className={styles.errorText}>Зачинено.</span> Відкриється о{" "}
      {hours.start}
    </div>
  );
}
