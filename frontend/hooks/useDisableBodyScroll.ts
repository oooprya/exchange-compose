import { useEffect } from "react";

// Basic Version
export function useDisableBodyScroll(active: boolean = true): void {
  useEffect(() => {
    if (!active) return;

    const originalStyle: string = window.getComputedStyle(
      document.body
    ).overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.body.style.overflow = originalStyle;
    };
  }, [active]);
}
