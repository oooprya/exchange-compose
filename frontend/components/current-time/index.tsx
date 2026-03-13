"use clinet";

export default function CurrentTime() {
  return <>{new Date().toLocaleDateString("ru-RU")}</>;
}
