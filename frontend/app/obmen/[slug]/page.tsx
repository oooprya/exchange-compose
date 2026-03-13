import { notFound } from "next/navigation";
import { RatesList } from "@/components/currency-rates/rates-list-slug";
import { Container } from "@/components/ui/container";
import ShareButton from '@/components/ui/share-button';
import { CardContainer } from '@/components/ui/card-container';
import CurrentTime from "@/components/current-time";
import ExchangersList from "@/components/exchangers-list";

import styles from "./page.module.css";
import type { Metadata } from "next";




// --- ОПТИМИЗАЦИЯ: Единая функция для загрузки данных ---
// Мы выносим логику fetch в отдельную функцию.
// Next.js автоматически дедуплицирует (выполнит только 1 раз)
// этот запрос для 'generateMetadata' и 'ExchangerPage'.
async function getExchangerData(slug: string) {
  const res = await fetch(
    `${process.env.NEXT_API_URL}/exchangers/?slug=${slug}`,
    {
      // --- ОПТИМИЗАЦИЯ КЭШИРОВАНИЯ ---
      // Вместо "no-store", мы используем ISR (Incremental Static Regeneration).
      // Страница будет статической и быстрой, но будет обновляться
      // в фоне каждые 60 секунд (или как вам нужно).
      next: { revalidate: 60 },
    }
  );

  // Простая обработка ошибок
  if (!res.ok) {
    console.error("Failed to fetch exchanger data:", res.statusText);
    return null;
  }

  const data = await res.json();

  if (!data.objects?.length) {
    return null;
  }

  return data.objects[0]; // Возвращаем сам объект
}

interface ExchangerPageProps {
  params: Promise<{ slug: string }>;
}
export async function generateMetadata({ params }: ExchangerPageProps): Promise<Metadata> {
  const { slug } = await params;
  // Используем нашу единую функцию
  const ex = await getExchangerData(slug);

  // Обработка случая, если обменник не найден
  if (!ex) {
    return {
      title: "Обмінник не знайдено",
    };
  }

  return {
    title: `Обмін валют – ${ex.address} | EXPRIVAT`,
    description: `Курс валют у пункті обміну: ${ex.address}. Актуальні курси, графік роботи та маршрут.`,
    metadataBase: new URL(`https://exprivat.com.ua/`),
    keywords:"курс долара Одеса, обмін валют Одеса, актуальний курс обміну, обмінники Одеса, курс євро до гривні",

    openGraph: {
      locale: "ua_UA",
      title: `Обмін валют – ${ex.address} | EXPRIVAT`,
      description: `Курс валют у пункті обміну: ${ex.address}. Актуальні курси, графік роботи та маршрут.`,
      type: "website",
      url: `https://exprivat.com.ua/obmen/${slug}`,
      images: {
        url: `address_${ex.id}.jpg`,
        width: "512px",
        height: "360px",
        alt: "Найкращий курс валют в Одесі сьогодні",
      },
      siteName: "exprivat.com.ua",
    },
    };
}


export default async function ExchangerPage({ params }: ExchangerPageProps) {
  const { slug } = await params;

  // Снова используем ту же функцию. Next.js возьмет данные из кэша.
  const exchanger = await getExchangerData(slug);

  // Если данные не найдены, вызываем 404
  if (!exchanger) {
    notFound();
  }

  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <Container>
          <div className={styles.inner}>
            <div className={styles.textWrapper}>
              <h1 className={styles.title}>
                Курс валют у пункті обміну: {exchanger.address}
              </h1>

              <p className={styles.pageP}>
                <strong>Графік роботи:</strong> {exchanger.working_hours}
              </p>
              <ShareButton
                  title={`Курс валют ${exchanger.address}`}
                  text={`Дивись актуальний курс валют у пункті обміну: ${exchanger.address}`}
                  url={`https://exprivat.com.ua/obmen/${exchanger.slug}`}
                />

            </div>

            <CardContainer>
              <div className={styles.col} itemScope itemType="https://schema.org/WebPage">
                <h2 className={styles.title}>
                  {/* <CurrentTime /> лучше тоже сделать клиентским компонентом,
                      чтобы он не ломал кэширование страницы */}
                  Курс валют на <CurrentTime /> 
                </h2>

                {/* ВАЖНО: Теперь <RatesList> должен сам 
                  загружать актуальные курсы! 
                  Внутри <RatesList> используйте fetch с { cache: "no-store" } 
                  или загружайте данные на клиенте (useEffect, SWR).
                */}
                <RatesList exchangerId={exchanger.id} />

                {/* JSON-LD Schema (без изменений) */}
                <script
                  type="application/ld+json"
                  dangerouslySetInnerHTML={{
                    __html: JSON.stringify({
                      "@context": "https://schema.org",
                      "@type": "FinancialService",
                      name: `Обмін валют ${exchanger.address}`,
                      address: exchanger.address,
                      openingHours: exchanger.working_hours,
                      url: `/obmin/${exchanger.slug}`,
                    }),
                  }}
                />
              </div>
            </CardContainer>
          </div>
        </Container>
      </section>

      <section>
        <Container>
          <div className={styles.info}>
            <ExchangersList />
          </div>
        </Container>
      </section>
    </div>
  );
}