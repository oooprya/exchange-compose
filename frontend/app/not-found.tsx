import Link from 'next/link'
import { Container } from "@/components/ui/container";
import { RatesList } from "@/components/currency-rates/rates-list";
import { CardContainer } from '@/components/ui/card-container';


import styles from "./page.module.css";

export default function NotFound() {
  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <Container>
          <div className={styles.inner}>
            
            <CardContainer>
                <div className={styles.col}>
                    <RatesList />
                </div>
            </CardContainer>
            <div className={styles.textWrapper}>
              <h1 className={styles.title}>
                Курс валют у Наших обмінниках на сьогодні
              </h1>
                <p className={styles.pageP}>
                  Завжди в наявності є гривня та валюта, якщо у Вас велика сума на замовлення ми обов&apos;язково вам надамо її
                </p>
                <p className={styles.pageP}>
                  Ми завжди стежимо за актуальним ринковим курсом валют, у нас ви можете обміняти за найвигіднішим курсом
                </p>
                <p className={styles.pageP}>
                  Ми пропонуємо нашим клієнтам найнижчу комісію за купівлю старої валюти, оскільки ми працюємо напряму без посередників.
                </p>
      
              
            <Link href="/" className={styles.button}>Як забронювати курс?</Link>
            </div>
          </div>
        </Container>
      </section>
    </div>
  )
}