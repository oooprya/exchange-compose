import { Container } from '../ui/container';
import { CardContainer } from '@/components/ui/card-container';
import styles from './index.module.css';


export function Contacts() {
  return (
    <section>
      <Container>
        <div className={styles.contactRow}>
          <span className={styles.contactText}>
            <h2 className={styles.servicesTitle}>Зв&apos;язок з нами</h2>
            <p className={styles.serviceText}>Наша команда завжди рада допомогти та відповісти на всі ваші запитання.</p>
            <p className={styles.serviceText}>Без вихідних</p>
          </span>
          <ul className={styles.contactList}>
            <li>
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
              
            </li>
            <li>
              <CardContainer>
              <div className={styles.Content}>
                <h3 className={styles.contactName}>Керівник</h3>
                <a href="tel:+380634765088" className={styles.contactTel} itemProp="telephone">063 476 50 88</a>
                <div className={styles.iconRow}>
                  <a href="https://t.me/VitalikPrivat" target="_blank" aria-label="посилання на telegram Керівника" className={styles.telegram}>&nbsp;</a>
                  <a href="https://wa.me/+380634765088" target="_blank" aria-label="посилання на whatsApp Керівника" className={styles.whatsApp}>&nbsp;</a>
                  <a href="viber://chat?number=%2B380634765088" target="_blank" aria-label="посилання на viber Керівника" className={styles.viber}>&nbsp;</a>
                </div>
              </div>
              </CardContainer>
              
            </li>
          </ul>
        </div>

      </Container>
    </section>
  );
}
