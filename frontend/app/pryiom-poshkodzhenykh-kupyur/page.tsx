// app/pryiom-poshkodzhenykh-kupyur/page.tsx
import Image from 'next/image'
import type { Metadata } from "next";
import { Container } from "@/components/ui/container";
import DamagedGallery from "@/components/damaged-gallery";
import { Services } from "@/components/services";
import { CardContainer } from '@/components/ui/card-container';
import CurrencyRates from "@/components/currency-rates";
import ExchangersList from "@/components/exchangers-list";


import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "Прийом пошкоджених купюр долара та євро в Одесі — від 1%",
  description:
    "Приймаємо пошкоджені, зношені долари та євро в Одесі. Купюри, які не беруть банки. Оцінка по фото, миттєва виплата.",
  metadataBase: new URL("https://www.exprivat.com.ua/"),
alternates: {
      canonical: `/pryiom-poshkodzhenykh-kupyur`,
    },
};
export default async function Home() {
  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <Container>
          <div className={styles.inner}>
            <div className={styles.textWrapper}>
              <h1 className={styles.title}>
                Ми приймаємо пошкоджені купюри долара і євро з найнижчою комісією в Одесі
              </h1>
              <p className={styles.subtitle}>
                *при обміні <span className={styles.textYellow}>від 500 дол.</span> з мінімальними пошкодженнями          (розрізи до 5 мм, печатки, пописані з мінімальними плямами)
              </p>
            </div>
            <Image className={styles.minPercent}
              src="/min_percent.png"
              width={550}
              height={480}
              alt="Від - 1% на сумі"
            />
          </div>
        </Container>
      </section>
      <section>
        <Container>
         
            <DamagedGallery />
          
        </Container>
      </section>

      <section>
        <Container>
          <h3 className={styles.stepsTitle}>
            Щоб оцінити стан вашої купюри — надішліть фото менеджеру
          </h3>
        <CardContainer>
          <div className={styles.Content}>
            
            <h3 className={styles.contactName}>Менеджер</h3>
            <a href="tel:+380967228090" className={styles.contactTel}>096 722 80 90</a>
            <div className={styles.iconRow}>
              <a href="https://t.me/PrivatObmenOd" target="_blank" aria-label="посилання на telegram Менеджера" className={styles.telegram}>&nbsp;</a>
              <a href="https://wa.me/+380967228090" target="_blank" aria-label="посилання на whatsApp Менеджера" className={styles.whatsApp}>&nbsp;</a>
              <a href="viber://chat?number=%2B380967228090" target="_blank" aria-label="посилання на viber Менеджера" className={styles.viber}>&nbsp;</a>
            </div>
          </div>
        </CardContainer>

        <p className={styles.subtitle}>
          Наш спеціаліст зв'яжеться з вами та відповість на всі запитання
        </p>
        </Container>
      </section>

      <section className={styles.servicesFaq}>
        <Container>
          <div className={styles.steps}>
            <h2 className={styles.stepsTitle}>Популярні запитання</h2>

            <ul className={styles.stepsList}>
              
              <li className={`${styles.stepsItem}`}>
                <h3 className={styles.stepsTitle}>Що означає грибок на купюрі?</h3>
                <p className={styles.stepsText}>Зовнішньо купюра може бути чиста, але це не означає, що вона гарної якості</p>
                <p className={styles.stepsText}>Для цього і існує детектор,в ньому видно всі дефекти купюри</p>
                <Image className={styles.imgFaq}
                  src="/damaged/poshkodzhea-kupyura_gribok.jpg"
                  width={1280}
                  height={960}
                  alt="Пошкоджені купюри долара з плямами та в грибоке"
                />
                <h4 className={styles.stepsText}>В даному випадку це грибок</h4>
              </li>
            </ul>
          </div>
          
        </Container>
      </section>
      <section>
        <Container>
          <div className={styles.info}>
            <ExchangersList />
            <CurrencyRates />
          </div>
        </Container>
      </section>
      <Services />

    </div>
  );
}
