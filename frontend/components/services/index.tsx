import Image from 'next/image';
import { Container } from '@/components/ui/container';
import { CardContainer } from '@/components/ui/card-container';
import styles from './index.module.css';

import { dataServices } from "@/data";

// ✨ Функция для случайного выбора N элементов
export function getRandomItems<T>(array: T[], count: number): T[] {
  const shuffled = [...array].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
}

type ServicesProps = {
  count?: number; // 👈 по умолчанию можно отобразить все
};

export function Services({ count = dataServices.length }: ServicesProps) {
  const services = getRandomItems(dataServices, count);
  return (
    <section id="services">
        <Container>
          <div className={styles.services}>
            <h2 className={styles.servicesTitle}>Наші послуги</h2>
            <ul className={styles.List}>
              {services.map((step) => (
                <li key={step.id}>
                  <CardContainer>
                    <div className={styles.serviceContent}>
                      <span><Image width={48} height={48} src={step.icon} alt={step.title} /></span>
                      <h3 className={styles.serviceTitle}>{step.title}</h3>
                      <p className={styles.serviceText}>{step.text}</p>
                    </div>
                  </CardContainer>
                </li>
              ))}
            </ul>
          </div>

        </Container>
    </section>
  );
}
