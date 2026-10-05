import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

/**
 * Las piezas que el diseño repite en cada tarjeta del panel.
 * Medidas de docs/design/manager.pen, frame «10. Dashboard».
 */

/** Tarjeta: radio 16, borde #dfe1e7, sombra 0 1px 1.75px. */
export function Widget({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <section
      className={cn(
        "flex flex-col overflow-hidden rounded-lg border border-border bg-card shadow-widget",
        className,
      )}
    >
      {children}
    </section>
  );
}

/**
 * Cabecera: 64 de alto, borde inferior, padding lateral 20.
 * El título va en texto secundario a propósito — en este diseño el nombre del
 * widget es recesivo y el protagonista es el dato.
 */
export function WidgetHeader({
  icon,
  title,
  children,
}: {
  icon: ReactNode;
  title: string;
  children?: ReactNode;
}) {
  return (
    <header className="flex h-16 flex-none items-center justify-between gap-4 border-b border-border px-5">
      <h2 className="flex items-center gap-2 text-base font-medium text-muted-foreground">
        <span className="flex size-5 flex-none items-center justify-center" aria-hidden="true">
          {icon}
        </span>
        <span className="truncate">{title}</span>
      </h2>
      {children}
    </header>
  );
}

/**
 * Píldora de variación. `basis` explica contra qué se compara: un porcentaje
 * sin denominador es una cifra que nadie puede auditar.
 */
export function DeltaPill({
  delta,
  basis,
  tone = "strong",
}: {
  delta: number | null;
  basis?: string;
  tone?: "strong" | "soft";
}) {
  if (delta === null || delta === undefined) {
    // Sin `basis` no hay comparacion definida para esta metrica: no va pildora.
    if (!basis) return null;
    return (
      <span
        className="inline-flex items-center rounded-full bg-accent px-2 py-px text-xs font-medium text-muted-foreground"
        title={`No hay periodo anterior contra el cual comparar (${basis})`}
      >
        sin base
      </span>
    );
  }

  const up = delta >= 0;
  const palette = up
    ? "bg-positive-soft text-positive"
    : tone === "strong"
      ? "bg-negative-strong-soft text-negative-strong"
      : "bg-negative-soft text-negative";

  return (
    <span
      className={cn(
        "inline-flex items-center gap-0.5 rounded-full py-px pl-1 pr-1.5 text-xs font-medium",
        palette,
      )}
      title={basis ? `${up ? "Sube" : "Baja"} ${Math.abs(delta)}% ${basis}` : undefined}
    >
      <Arrow up={up} />
      {Math.abs(delta)}%
    </span>
  );
}

/** La flecha del .pen: diagonal con cola, 14x14, trazo 1.167. */
function Arrow({ up }: { up: boolean }) {
  return (
    <svg viewBox="0 0 14 14" className="size-3.5 flex-none" aria-hidden="true">
      <path
        d={up ? "M3.5 10.5l7-7m0 7v-7h-7" : "M3.5 3.5l7 7m0-7v7h-7"}
        fill="none"
        stroke="currentColor"
        strokeWidth="1.167"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
