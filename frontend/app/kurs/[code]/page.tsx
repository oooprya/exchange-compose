import { MainForm } from "@/components/main-form";
import { Container } from "@/components/ui/container";
import { Services } from "@/components/services";
import { RatesList } from "@/components/currency-rates/rates-list-ssr";
import { CardContainer } from '@/components/ui/card-container';
import ExchangersList from "@/components/exchangers-list";
import ExchangersResult from "@/components/exchangers-result";

import type { Currency } from "@/types";
import type { Metadata } from 'next'

import styles from "./page.module.css";


import { notFound } from 'next/navigation';


async function getCurrencyIdByCode(code: string): Promise<number | null> {
  const res = await fetch(`${process.env.NEXT_API_URL}/currency/?limit=23`, {
    next: { revalidate: 60 },
  });
  const data = await res.json() as {objects: Currency[]};

  const found = data.objects.find(
    item => {
            return item.code === code
          }
  );

  return found ? found.id : null;
}

async function getCurrencyDataById(id: number) {
  const res = await fetch(`${process.env.NEXT_API_URL}/currencys/?currency=${id}`, {
    next: { revalidate: 60 },
  });
  const data = await res.json();
  return data.objects[0]; // только первый курс
}

type Props = {
  params: Promise<{ code: string }>
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>
}
export async function generateMetadata(
  { params }: Props): Promise<Metadata> {
  const { code } = await params
  try {
    const res = await fetch(`${process.env.NEXT_API_URL}/currency/`, {
      next: { revalidate: 60 },
    });

    if (!res.ok) throw new Error('API failed');

    const data = (await res.json()) as { objects: Currency[] };

    const currency = data.objects.find((item) => item.code === code);

    if (!currency) {
      return {
        title: 'Курс валют у центрі одесі',
        description: 'Обмін валют за найкращим курсом.',
      };
    }

    return {
      title: `Курс ${currency.name} - обмін валют у центрі одесі`,
      description: `Актуальний курс ${currency.name} в Одесі. Купівля та продаж за вигідним курсом. Бронюй онлайн або знайди зручне відділення.`,
    };
  } catch (error) {
    console.error('Metadata fetch error:', error);
    return {
      title: 'Курс валют',
      description: 'Обмін валют в Одесі.',
    };
  }
}


export default async function CurrencyPage({
  params,
}: {
  params: Promise<{ code: string }>
}) {

  const { code } = await params
  const currencyId = await getCurrencyIdByCode(code);
  if (!currencyId) notFound();

  const currency = await getCurrencyDataById(currencyId);
  if (!currency) notFound();


  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <Container>
          <div className={styles.inner}>
               <div className={styles.textWrapper}>
                <h1 className={styles.title}>
                  Оптовий курс {currency.currency_name} від 500 - Одеса
                </h1>

                 <div className={styles.Card}>
                    <div className={styles.grid}>
                      <p className={styles.pageP}>Купівля</p>
                      <p className={styles.pageP}>Продаж</p>
                    </div>
                    <div className={styles.grid}>
                      <p className={styles.rate}>{currency.buy}</p>
                      <p className={styles.rate}>{currency.sell}</p>
                    </div>
                    <p className={styles.pageP}>Обновлено: {new Date(currency.updatedAt).toLocaleString("uk-UA", {
                      timeZone: "Europe/Kiev",
                      hour: "2-digit",
                      minute: "2-digit",
                      day: "2-digit",
                      month: "2-digit",
                      year: "numeric",})}</p>
                 </div>
                  <p className={styles.pageP}>
                     Якщо ви шукаєте надійний та вигідний обмін валют в Одесі, ви потрапили за адресою.
                     Ми пропонуємо актуальний курс долара USD, євро EUR, злотого PLN та інших популярних валют у зручних локаціях міста.
                  </p>
              </div>
              <MainForm />
             </div>
        </Container>
      </section>
      <ExchangersResult />
      <Services count={3}/>
      <section>
        <Container>
          <div className={styles.info}>
            <CardContainer>
                <div className={styles.col} itemScope itemType="https://schema.org/WebPage">
                    <RatesList />
                </div>
            </CardContainer>
            <ExchangersList />
          </div>
        </Container>
      </section>
    </div>
  );
}





