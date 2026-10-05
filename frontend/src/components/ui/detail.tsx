import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

/** Las piezas que comparten las dos pantallas de detalle del .pen. */

export type Tone = "success" | "warning" | "error" | "neutral";

/** Cabecera: retrato a la izquierda, identidad al centro, acciones a la derecha. */
export function DetailHero({
  portrait,
  title,
  badges,
  meta,
  actions,
}: {
  portrait: ReactNode;
  title: string;
  badges: { label: string; tone: Tone }[];
  meta: { icon: LucideIcon; value: string }[];
  actions?: ReactNode;
}) {
  return (
    <section className="flex flex-wrap items-center gap-5 rounded-lg border border-border bg-card p-5 shadow-widget">
      {portrait}
      <div className="flex min-w-0 flex-1 flex-col gap-1.5">
        <div className="flex flex-wrap items-center gap-2">
          <h1 className="text-2xl font-semibold text-foreground">{title}</h1>
          {badges.map((badge) => (
            <Badge key={badge.label} dot variant={badge.tone}>
              {badge.label}
            </Badge>
          ))}
        </div>
        <ul className="flex flex-wrap items-center gap-x-4 gap-y-1">
          {meta.map(({ icon: Icon, value }) => (
            <li key={value} className="flex items-center gap-1.5 text-sm text-muted-foreground">
              <Icon className="size-4 flex-none text-faint" aria-hidden="true" />
              {value}
            </li>
          ))}
        </ul>
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </section>
  );
}

/** Campo del formulario de la ficha. El error va debajo y marca el control. */
export function Field({
  name,
  label,
  error,
  children,
  hint,
}: {
  name: string;
  label: string;
  error?: string;
  hint?: string;
  children?: ReactNode;
}) {
  return (
    <div className="flex min-w-0 flex-1 flex-col gap-1.5" data-invalid={error ? "" : undefined}>
      <Label htmlFor={name} className="text-xs font-medium text-muted-foreground">
        {label}
      </Label>
      {children}
      {hint && !error && <p className="text-xs text-faint">{hint}</p>}
      {error && (
        <p id={`${name}-error`} className="text-xs text-destructive">
          {error}
        </p>
      )}
    </div>
  );
}

export function TextField({
  name,
  label,
  defaultValue,
  error,
  type = "text",
  hint,
  ...rest
}: {
  name: string;
  label: string;
  defaultValue?: string | number;
  error?: string;
  type?: string;
  hint?: string;
} & React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <Field name={name} label={label} error={error} hint={hint}>
      <Input
        id={name}
        name={name}
        type={type}
        defaultValue={defaultValue ?? ""}
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? `${name}-error` : undefined}
        className="h-10 rounded-md"
        {...rest}
      />
    </Field>
  );
}

export function SelectField({
  name,
  label,
  defaultValue,
  options,
  error,
  onChange,
}: {
  name: string;
  label: string;
  defaultValue?: string;
  options: { value: string; label: string }[];
  error?: string;
  onChange?: (value: string) => void;
}) {
  return (
    <Field name={name} label={label} error={error}>
      <select
        id={name}
        name={name}
        defaultValue={defaultValue}
        onChange={onChange ? (event) => onChange(event.target.value) : undefined}
        aria-invalid={error ? true : undefined}
        className="h-10 rounded-md border border-input bg-background px-3 text-sm text-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </Field>
  );
}

/** Pie de la ficha: la nota a la izquierda, guardar a la derecha. */
export function FormFooter({ hint, children }: { hint: string; children: ReactNode }) {
  return (
    <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-border bg-secondary px-5 py-3.5">
      <p className="text-xs text-muted-foreground">{hint}</p>
      <div className="flex items-center gap-2">{children}</div>
    </footer>
  );
}

/** Fila clave → valor de las tarjetas laterales. */
export function KeyValue({ term, children }: { term: string; children: ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <dt className="text-sm text-muted-foreground">{term}</dt>
      <dd className="text-sm font-medium tabular-nums text-foreground">{children}</dd>
    </div>
  );
}

/**
 * Barras por semana. Una sola serie en un solo hue, sin leyenda: el título la
 * nombra. El valor va en el title de cada barra, que es la vista de tabla que
 * el contraste del verde obliga a tener.
 */
export function WeekBars({
  points,
  suffix = "",
}: {
  points: { label: string; value: number }[];
  suffix?: string;
}) {
  const max = Math.max(...points.map((p) => p.value), 1);
  return (
    <div className="flex h-28 items-end gap-1" role="img" aria-label="Actividad por semana">
      {points.map((point) => (
        // La columna lleva h-full: sin altura en el padre, el % de la barra no
        // resuelve contra nada y el grafico sale vacio.
        <div key={point.label} className="flex h-full min-w-0 flex-1 flex-col gap-1.5">
          <div className="flex min-h-0 flex-1 items-end">
            <div
              className={cn("w-full rounded-t-sm", point.value ? "bg-primary" : "bg-accent")}
              style={{ height: `${Math.max((point.value / max) * 100, 3)}%` }}
              title={`Semana ${point.label}: ${point.value}${suffix}`}
            />
          </div>
          <span className="text-center text-[0.625rem] tabular-nums text-faint">
            {point.label}
          </span>
        </div>
      ))}
    </div>
  );
}
