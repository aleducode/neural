import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

import { SidebarMenuButton } from "@/components/ui/sidebar";

/**
 * «Dark Mode» del pie del sidebar (nodo #Crt92 del .pen).
 *
 * El tema vive en data-theme sobre <html> y se recuerda en localStorage. Se
 * aplica en el primer render, no en un efecto, para no pintar el panel claro y
 * saltar a oscuro medio segundo despues.
 */

const KEY = "neural-manager-theme";

function leer(): "light" | "dark" {
  if (typeof document === "undefined") return "light";
  const guardado = localStorage.getItem(KEY);
  if (guardado === "dark" || guardado === "light") return guardado;
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function applyStoredTheme() {
  document.documentElement.dataset.theme = leer();
}

export function ThemeToggle() {
  const [theme, setTheme] = useState<"light" | "dark">(() => leer());

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem(KEY, theme);
  }, [theme]);

  const dark = theme === "dark";
  return (
    <SidebarMenuButton
      onClick={() => setTheme(dark ? "light" : "dark")}
      aria-pressed={dark}
      tooltip={dark ? "Modo claro" : "Modo oscuro"}
      className="h-9 gap-2.5 rounded-md px-3 text-sm font-medium text-muted-foreground [&>svg]:size-[18px]"
    >
      {dark ? <Sun /> : <Moon />}
      <span>{dark ? "Modo claro" : "Modo oscuro"}</span>
    </SidebarMenuButton>
  );
}
