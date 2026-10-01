import Link from "next/link";

import { Container } from "@/components/ui/container";
import Logo from "@/components/ui/icons/logo";

import styles from "./index.module.css";

export function Header() {
  return (
    <header className={styles.header}>
      <Container>
        <nav className={styles.nav}>
          <Link className={styles.logo} href="/" title="Главная страница">
            <Logo className={styles.logoImg} />
            <strong>Private</strong> <span>exchanges</span>
          </Link>
          <Link
            className={styles.navlink}
            href="/bank-metals"
            title="Банківські метали">
            Банківські метали
          </Link>
          
        </nav>
      </Container>
    </header>
  );
}
