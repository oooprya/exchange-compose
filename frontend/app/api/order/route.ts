import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const body = await request.json();

    const res = await fetch(`${process.env.NEXT_API_URL!}/orders/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `ApiKey ${process.env.NEXT_API_KEY}`,
      },
      body: JSON.stringify(body), // Передаём в body
    });

    if (!res.ok) throw new Error("Помилка при створенні замовлення");

    const data = await res.json();

    return NextResponse.json(data, { status: 201 });
  } catch (error) {
    return NextResponse.json(
      {
        error: `Помилка сервера при створенні замовлення ${
          error instanceof Error && error.message
        }`,
      },
      { status: 500 }
    );
  }
}
