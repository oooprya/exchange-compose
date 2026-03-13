import styles from "./index.module.css";

type FormTabsProps = {
  mode: "buy" | "sell";
  setMode: (mode: "buy" | "sell") => void;
};

export function FormTabs({ mode, setMode }: FormTabsProps) {
  const buyBtnClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (mode !== "buy") {
      setMode("buy");
    }
  };

  const sellBtnClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (mode !== "sell") {
      setMode("sell");
    }
  };
  return (
    <nav className={styles.tabs}>
      <button
        className={styles.navBtn}
        onClick={buyBtnClick}
        disabled={mode === "buy"}
      >
        Продати
      </button>
      <button
        className={styles.navBtn}
        onClick={sellBtnClick}
        disabled={mode === "sell"}
      >
        Купити
      </button>
    </nav>
  );
}
