import { NextResponse } from "next/server";

export async function GET() {
  const preliminaryRes = await fetch(`${process.env.NEXT_API_URL}/currency/`);
  const preliminaryData = await preliminaryRes.json();
  const { total_count: total } = preliminaryData.meta;

  const res = await fetch(
    `${process.env.NEXT_API_URL}/currency/?limit=${total}`
  );
  const data = await res.json();

  return NextResponse.json(data);
}
