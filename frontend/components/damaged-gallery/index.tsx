// components/DamagedGallery.tsx
import Image from "next/image";
import styles from "./index.module.css";

const images = [
  {
    src: "/damaged/1.jpg",
    alt: "Підгорілі купюри долара США з потертостями та слідами використання",
  },
  {
    src: "/damaged/2.jpg",
    alt: "Сильно пошкоджені купюри долара США з плямами та розривами",
  },
  {
    src: "/damaged/3.jpg",
    alt: "Пошкоджені купюри долара США з надривами та деформаціями",
  },
  {
    src: "/damaged/4.jpg",
    alt: "Старі та потерті долари, які приймають в обміннику в Одесі",
  },
  {
    src: "/damaged/5.jpg",
    alt: "Частково згорілі купюри з плямами та слідами зношення",
  },
  {
    src: "/damaged/6.jpg",
    alt: "Частково згорілі купюри доларив",
  },
  {
    src: "/damaged/7.jpg",
    alt: "Зношені купюри євро з потертостями та пошкодженнями",
  },
  {
    src: "/damaged/8.jpg",
    alt: "Старі та пошкоджені купюри євро різного номіналу для обміну",
  },
];

export default function DamagedGallery() {
  return (
    <section className="bg-black py-14">
      <div className="container mx-auto px-4">
        {/* TITLE */}
        <h2 className={styles.h2}>
          Навіть <span className={styles.textYellow}>такі купюри</span> ми візьмемо у вас
        </h2>

        {/* GRID */}
        <div className={styles.grid}>
          {images.map((image, index) => (
            <div
              key={index}
              className="relative overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900"
            >
              <Image
                src={image.src}
                alt={image.alt}
                width={270}
                height={360}
                className="h-full w-full object-cover transition-transform duration-300 hover:scale-105"
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
