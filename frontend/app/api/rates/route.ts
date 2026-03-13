import { Rates } from "@/types";
import { NextResponse } from "next/server";

export async function GET() {
  try {
    const preliminaryRes = await fetch(`${process.env.NEXT_API_URL}/currency/`);
    const preliminaryData = await preliminaryRes.json();
    const { total_count: total } = preliminaryData.meta;

    const res = await fetch(
      `${process.env.NEXT_API_URL}/currencys/?limit=${total}`
    );

    const { objects: rates }: { objects: Rates[] } = await res.json();
    return NextResponse.json(rates);
  } catch (error) {
    throw new Error(
      `Failed to fetch exchangers list: ${
        error instanceof Error && error.message
      }`
    );
  }
}
