import { NextResponse } from "next/server";
import { Currency } from "@/types";

export async function GET() {
  try {
    const res = await fetch(`${process.env.NEXT_API_URL}/currencys/`);

    const { objects }: { objects: Currency[] } = await res.json();
    return NextResponse.json(objects);
  } catch (error) {
    throw new Error(
      `Failed to fetch currency list: ${
        error instanceof Error && error.message
      }`
    );
  }
}
