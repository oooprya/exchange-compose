import SimpleBar from "simplebar-react";
import { Currency } from "@/types";
import styles from "./index.module.css";

type SelectDropdownProps = {
  options: Currency[] | null;
  handleOptionClick: (option: Currency) => void;
};

export function SelectDropdown({
  options,
  handleOptionClick,
}: SelectDropdownProps) {
  return (
    <SimpleBar className={styles.options}>
      <ul className={styles.list}>
        {options?.map((option) => (
          <li
            className={styles.option}
            key={option.id}
            onClick={() => {
              handleOptionClick(option);
            }}
          >
            {option.name}
          </li>
        ))}
      </ul>
    </SimpleBar>
  );
}
