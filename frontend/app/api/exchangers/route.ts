import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const currencyId = searchParams.get("currencyId");
  const sum = searchParams.get("sum");

  let query = "";

  if (Number(sum) < 500) {
    query = `currency=${currencyId}&sum__lt=500`;
  } else {
    query = `currency=${currencyId}&sum__gte=${sum}`;
  }

  const res = await fetch(`${process.env.NEXT_API_URL!}/currencys/?${query}`);
  const data = await res.json();
  return NextResponse.json(data);
}
