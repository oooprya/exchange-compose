// components/DamagedGallery.tsx
import Image from "next/image";
import styles from "./index.module.css";


// Определяем типы для пропсов
interface ProductItemProps {
  imageSrc: string;
  title: string; // Например: "Золотий злиток 1 унц."
  // price: string; // Например: "263 513 грн"
  width?: number; // Опционально, дефолт 225
  height?: number; // Опционально, дефолт 225
}

export default function ProductItem({
  imageSrc,
  title,
  // price,
  width = 225,
  height = 225,
}: ProductItemProps) {
  return (
    
    <li className={`${styles.stepsItem}`}>
      <Image
        className={styles.minPercent}
        src={imageSrc}
        width={width}
        height={height}
        alt={title} // Alt должен описывать изображение (лучше всего брать заголовок)
        priority={false} // Поставьте true, если это первое изображение на экране (LCP)
      />
      <div className={styles.stepsContent}>
        <p className={styles.stepsText}>{title}</p>
        {/* <h3 className={styles.stepsTitle}>{price}</h3> */}
      </div>
    </li>
  );
}