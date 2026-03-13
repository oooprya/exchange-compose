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
            Private <span>exchanges</span>
          </Link>
        </nav>
      </Container>
    </header>
  );
}
