import Image from 'next/image';
import type { Metadata } from "next";
import { Container } from "@/components/ui/container";
import ProductItem from '@/components/services-metal';
import { dataStepsMetal } from "@/data";


import styles from "./page.module.css";

// Пример массива данных
  const products = [
    {
      id: 1,
      name: 'Золотий злиток 1 унц.',
      // price: '263 513 грн',
      img: '/zolotyy-zlytok-1-unts.png',
    },
    {
      id: 2,
      name: 'Золотий злиток 10 г',
      // price: '421 493 грн',
      img: '/zolotyy-zlytok-10-h.png',
    },
    {
      id: 3,
      name: 'Золотий злиток 20 г',
      // price: '421 493 грн',
      img: '/zolotyy-zlytok-20-h.png',
    },
    {
      id: 4,
      name: 'Золотий злиток 50 г',
      // price: '421 493 грн',
      img: '/zolotyy-zlytok-50-h.png',
    },
    {
      id: 5,
      name: 'Золотий злиток 100 г',
      // price: '838 662 грн',
      img: '/zolotyy-zlytok-100-h.png',
    },
  ];
  const productsAg = [
    {
      id: 1,
      name: 'Злиток срібний 100 г.',
      // price: '50 701 грн',
      img: '/zlytok-sribnyy-100-h.png',
    },
    {
      id: 2,
      name: 'Злиток срібний 250 г.',
      // price: '50 701 грн',
      img: '/zlytok-sribnyy-250-h.png',
    },
    {
      id: 3,
      name: 'Злиток срібний 500 г.',
      // price: 'Передзамовлення',
      img: '/zlytok-sribnyy-500-h.png',
    },
    {
      id: 4,
      name: 'Злиток срібний 1000 г.',
      // price: '237 325 грн',
      img: '/zlytok-sribnyy-1000-h.png',
    },
  ];

export const metadata: Metadata = {
  title: "Інвестиційне золото та срібло в Одесі – Купити злитки",
  description:
    "Золоті та срібні злитки в наявності. Інвестуйте у метали, яким довіряють. Найкращі ціни в Одесі та доставка по Україні. Надійність гарантовано.",
  metadataBase: new URL("https://www.exprivat.com.ua/"),
alternates: {
      canonical: `/bank-metals`,
  },
    openGraph: {
    locale: "ua_UA",
    title: "Купуємо та продаємо золоті, срібні злитки в Одесі",
    description:
      "Золоті та срібні злитки в наявності. Інвестуйте у метали, яким довіряють. Найкращі ціни в Одесі та доставка по Україні. Надійність гарантовано.",
    type: "website",
    url: "https://www.exprivat.com.ua/bank-metals",
    images: {
      url: "/bank-metals-banner.jpg",
      width: "600px",
      height: "420px",
      alt: "Інвестиційне золото та срібло в Одесі",
    },
    siteName: "exprivat.com.ua",
  },
};
export default async function Home() {
  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <Container>
          <div className={styles.inner}>
            <Image
              className={styles.imgbankMetals} 
              src={`/bank-metals-banner.jpg`}
              width={600}
              height={420}
              alt="Інвестиційне золото та срібло в Одесі"
              priority={false}
            />
            <div className={styles.textWrapper}>
              <h1 className={styles.title}>
                Купуємо та продаємо золоті, срібні злитки в Одесі
              </h1>
              <p className={styles.subtitle}>
                Інвестуй в майбутнє якому довіряють у всьому світі
              </p>

              <div className={styles.Content}>
                <div className={styles.contactName}>Напишіть менеджеру або зателефонуйте:</div>
                <div className={styles.iconRow}>
                  <a href="https://t.me/VitalikPrivat" target="_blank" aria-label="посилання на telegram Керівника" className={styles.telegram}>&nbsp;</a>
                  <a href="https://wa.me/+380634765088" target="_blank" aria-label="посилання на whatsApp Керівника" className={styles.whatsApp}>&nbsp;</a>
                  <a href="viber://chat?number=%2B380634765088" target="_blank" aria-label="посилання на viber Керівника" className={styles.viber}>&nbsp;</a>
                </div>
                <a href="tel:+380634765088" className={styles.contactTel} itemProp="telephone">063 476 50 88</a>
              </div>
            </div>
          </div>
        </Container>
      </section>

       <section className={styles.dataStepsMetal}>
        <Container>
          <div className={styles.steps}>
            <h2 className={styles.stepsTitle}>Чому саме ми?</h2>
            <ul className={styles.stepsList}>
              {dataStepsMetal.map((step, index) => (
                <li className={styles.stepsItem} key={step.id}>
                  <span className={styles.stepsNumber}>{index + 1}</span>
                  <div className={styles.stepsContent}>
                    <h3 className={styles.stepTitle}>{step.title}</h3>
                    <p className={styles.stepsText}>{step.text}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </Container>
      </section>


      <section className={styles.servicesMetal}>
        <Container>
          <div className={styles.steps}>
            <h2 className={styles.stepsTitle}>Золото</h2>

            <ul className={styles.stepsList}>
              {products.map((product) => (
                <ProductItem
                  key={product.id}
                  imageSrc={product.img}
                  title={product.name}
                  // price={product.price}
                />
              ))}
            
          </ul>
          </div>
          
        </Container>
      </section>

      <section className={styles.servicesMetalSiver}>
        <Container>
          <div className={styles.steps}>
            <h2 className={styles.stepsTitle}>Срібло</h2>

            <ul className={styles.stepsList}>
              {productsAg.map((product) => (
                <ProductItem
                  key={product.id}
                  imageSrc={product.img}
                  title={product.name}
                  // price={product.price}
                />
              ))}
            
          </ul>
          </div>
          
        </Container>
      </section>

      <section className={styles.servicesFaq}>
        <Container>
          <div className={styles.steps}>
            <h2 className={styles.stepsTitle}>Популярні запитання</h2>

            <ul className={styles.stepsList}>
              <li className={`${styles.stepsItem}`}>
                <h3 className={styles.stepsTitle}>Чи можна викупити виріб назад?</h3>
                <p className={styles.stepsText}>Так. Для уточнення умов, зверніться до менеджера за телефоном, вказанним на сайті.</p>
              </li>
              <li className={`${styles.stepsItem}`}>
                <h3 className={styles.stepsTitle}>Купуєте ви антикваріат?</h3>
                <p className={styles.stepsText}>Ні, антикваріат не купуємо, тільки золото чи срібло в злитках</p>
              </li>
              <li className={`${styles.stepsItem}`}>
                <h3 className={styles.stepsTitle}>Від чого буде залежати ціна злитків?</h3>
                <p className={styles.stepsText}>Ціна залежить від проби,стану виробу,наявності камінців та цін на фондовому ринку</p>
              </li>
            </ul>
          </div>
          
        </Container>
      </section>


    </div>
  );
}
