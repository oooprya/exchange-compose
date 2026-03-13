import { Container } from '../ui/container';
import styles from './index.module.css';

export function Footer() {
  return (
    <footer className={styles.footer}>
      <Container>
        <div className={styles.copyright}>
          &copy; 2022 - {new Date().getFullYear()} Обмін валют
        </div>
      </Container>
    </footer>
  );
}
