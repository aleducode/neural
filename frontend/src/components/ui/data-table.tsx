import { ChevronLeft, ChevronRight, Search } from "lucide-react";
import { useMemo, type ReactNode } from "react";

import { Input } from "@/components/ui/input";
import { Widget, WidgetHeader } from "@/components/ui/widget";
import { cn } from "@/lib/utils";

/**
 * La tarjeta de tabla que el .pen repite en Members, Classes, Bookings y
 * Transactions: cabecera de 64 con buscador de 256, la tabla, y la paginacion
 * de 64 abajo («Showing 1 to 8 of, 473 results» + per page + numeros).
 *
 * Filtrar y paginar pasan por el cliente: son cientos de filas, caben de sobra
 * en una respuesta, y asi cada tecla deja de recargar la pagina.
 */

/** Filtra, pagina y devuelve lo que la tabla tiene que pintar. */
export function usePagedRows<T>(
  rows: T[],
  query: string,
  matches: (row: T, needle: string) => boolean,
  pageSize: number,
  page: number,
) {
  return useMemo(() => {
    const needle = query.trim().toLowerCase();
    const filtered = needle ? rows.filter((row) => matches(row, needle)) : rows;
    const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
    const current = Math.min(page, pages);
    const from = (current - 1) * pageSize;
    return {
      visible: filtered.slice(from, from + pageSize),
      total: filtered.length,
      pages,
      current,
      from: filtered.length ? from + 1 : 0,
      to: Math.min(from + pageSize, filtered.length),
    };
  }, [rows, query, matches, pageSize, page]);
}

export function DataTableCard({
  icon,
  title,
  searchPlaceholder,
  query,
  onQuery,
  actions,
  children,
}: {
  icon: ReactNode;
  title: string;
  searchPlaceholder: string;
  query: string;
  onQuery: (value: string) => void;
  actions?: ReactNode;
  children: ReactNode;
}) {
  return (
    <Widget>
      <WidgetHeader icon={icon} title={title}>
        <div className="flex w-full items-center gap-2 sm:w-auto">
          <div className="relative flex-1 sm:flex-none">
            <Search
              className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
              aria-hidden="true"
            />
            <Input
              type="search"
              value={query}
              onChange={(event) => onQuery(event.target.value)}
              placeholder={searchPlaceholder}
              aria-label={searchPlaceholder}
              className="h-8 w-full rounded-md pl-9 text-xs sm:w-64"
            />
          </div>
          {actions}
        </div>
      </WidgetHeader>
      {children}
    </Widget>
  );
}

/**
 * Paginacion del diseño. Los numeros van en un grupo con borde compartido y el
 * activo en verde; los controles son dos cuadrados de 32 a los lados.
 */
export function TablePagination({
  from,
  to,
  total,
  page,
  pages,
  pageSize,
  onPage,
  onPageSize,
  noun = "resultados",
}: {
  from: number;
  to: number;
  total: number;
  page: number;
  pages: number;
  pageSize: number;
  onPage: (page: number) => void;
  /** Sin esto no se dibuja el selector: cuando el tamaño lo fija el servidor,
   *  un desplegable que no hace nada es peor que su ausencia. */
  onPageSize?: (size: number) => void;
  noun?: string;
}) {
  return (
    <nav
      className="flex h-16 flex-wrap items-center justify-between gap-4 px-5 py-4"
      aria-label="Paginación"
    >
      <p className="text-sm font-medium text-foreground">
        {total === 0
          ? `Sin ${noun}`
          : `Mostrando ${from} a ${to} de ${total.toLocaleString("es-CO")} ${noun}`}
      </p>

      <div className="flex flex-wrap items-center gap-2">
        {onPageSize && (
        <label className="flex h-8 items-center overflow-hidden rounded-md border border-border text-xs font-medium">
          <span className="border-r border-border px-2 py-2 text-foreground">Por página</span>
          <select
            value={pageSize}
            onChange={(event) => {
              onPageSize(Number(event.target.value));
              onPage(1);
            }}
            className="h-full bg-transparent px-2 text-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
            aria-label="Filas por página"
          >
            {[10, 20, 50, 100].map((size) => (
              <option key={size} value={size}>
                {size}
              </option>
            ))}
          </select>
        </label>
        )}

        <div className="flex items-center gap-2">
          <PageControl
            label="Página anterior"
            disabled={page <= 1}
            onClick={() => onPage(page - 1)}
          >
            <ChevronLeft className="size-5" />
          </PageControl>

          <div className="flex items-center overflow-hidden rounded-md border border-border">
            {pageNumbers(page, pages).map((item, index) =>
              item === "…" ? (
                <span
                  key={`gap-${index}`}
                  className="flex size-8 items-center justify-center border-r border-border text-xs font-medium text-foreground last:border-r-0"
                >
                  …
                </span>
              ) : (
                <button
                  key={item}
                  type="button"
                  onClick={() => onPage(item)}
                  aria-current={item === page ? "page" : undefined}
                  className={cn(
                    "flex size-8 items-center justify-center border-r border-border text-xs font-medium last:border-r-0",
                    item === page
                      ? "bg-primary text-primary-foreground"
                      : "text-foreground hover:bg-secondary",
                  )}
                >
                  {item}
                </button>
              ),
            )}
          </div>

          <PageControl
            label="Página siguiente"
            disabled={page >= pages}
            onClick={() => onPage(page + 1)}
          >
            <ChevronRight className="size-5" />
          </PageControl>
        </div>
      </div>
    </nav>
  );
}

function PageControl({
  label,
  disabled,
  onClick,
  children,
}: {
  label: string;
  disabled: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-label={label}
      className="flex size-8 items-center justify-center rounded-md border border-border text-foreground disabled:opacity-40 hover:bg-secondary disabled:hover:bg-transparent"
    >
      {children}
    </button>
  );
}

/** 1 … 4 [5] 6 … 20 — nunca mas de siete casillas. */
function pageNumbers(page: number, pages: number): (number | "…")[] {
  if (pages <= 7) return Array.from({ length: pages }, (_, i) => i + 1);
  const out: (number | "…")[] = [1];
  const start = Math.max(2, page - 1);
  const end = Math.min(pages - 1, page + 1);
  if (start > 2) out.push("…");
  for (let i = start; i <= end; i++) out.push(i);
  if (end < pages - 1) out.push("…");
  out.push(pages);
  return out;
}
