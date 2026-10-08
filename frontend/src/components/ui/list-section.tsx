import { useState, type ReactNode } from "react";

import { DataTableCard, TablePagination, usePagedRows } from "@/components/ui/data-table";
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty";
import { PageHeader } from "@/components/ui/page-header";
import { StatWidget, type Kpi } from "@/components/ui/stat-widget";
import { Table, TableHead } from "@/components/ui/table";

/**
 * La pantalla de lista del .pen, entera: cabecera, cuatro KPI, tarjeta de tabla
 * con buscador y paginacion. Members, Classes, Bookings, Payments y Plans son
 * la misma pantalla con otra tabla adentro, asi que viven todas de aqui.
 */

export type Column = { label: string; className?: string };

type Props<T> = {
  title: string;
  description: string;
  actions?: ReactNode;
  kpis: Kpi[];
  tableIcon: ReactNode;
  tableTitle: string;
  searchPlaceholder: string;
  /** Lo que el buscador compara. Se arma una sola vez por fila. */
  haystack: (row: T) => string;
  rows: T[];
  columns: Column[];
  renderRow: (row: T, index: number) => ReactNode;
  rowKey: (row: T) => string | number;
  noun: string;
  minWidth?: string;
  emptyIcon: ReactNode;
  emptyTitle: string;
  emptyDetail: string;
  /** Nota al pie de la tarjeta: de que periodo habla la tabla, por ejemplo. */
  footnote?: ReactNode;
};

export function ListSection<T>({
  title,
  description,
  actions,
  kpis,
  tableIcon,
  tableTitle,
  searchPlaceholder,
  haystack,
  rows,
  columns,
  renderRow,
  rowKey,
  noun,
  minWidth = "720px",
  emptyIcon,
  emptyTitle,
  emptyDetail,
  footnote,
}: Props<T>) {
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  const paged = usePagedRows(
    rows,
    query,
    (row, needle) => haystack(row).toLowerCase().includes(needle),
    pageSize,
    page,
  );

  return (
    <div className="flex flex-col gap-6">
      <PageHeader title={title} description={description}>
        {actions}
      </PageHeader>

      <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.map((kpi) => (
          <StatWidget {...kpi} key={kpi.key} />
        ))}
      </div>

      <DataTableCard
        icon={tableIcon}
        title={tableTitle}
        searchPlaceholder={searchPlaceholder}
        query={query}
        onQuery={(value) => {
          setQuery(value);
          setPage(1);
        }}
      >
        {paged.total === 0 ? (
          <Empty>
            <EmptyHeader>
              <EmptyMedia variant="icon">{emptyIcon}</EmptyMedia>
              <EmptyTitle>{query ? `Sin resultados para «${query}»` : emptyTitle}</EmptyTitle>
              <EmptyDescription>
                {query ? "Probá con otro nombre, email o referencia." : emptyDetail}
              </EmptyDescription>
            </EmptyHeader>
          </Empty>
        ) : (
          <>
            <Table style={{ minWidth }}>
              <thead>
                <tr>
                  {columns.map((column) => (
                    <TableHead key={column.label} className={column.className}>
                      {column.label}
                    </TableHead>
                  ))}
                </tr>
              </thead>
              <tbody>
                {paged.visible.map((row, index) => (
                  <tr
                    key={rowKey(row)}
                    className="border-b border-border transition-colors last:border-0 hover:bg-secondary"
                  >
                    {renderRow(row, paged.from + index)}
                  </tr>
                ))}
              </tbody>
            </Table>

            <TablePagination
              from={paged.from}
              to={paged.to}
              total={paged.total}
              page={paged.current}
              pages={paged.pages}
              pageSize={pageSize}
              onPage={setPage}
              onPageSize={setPageSize}
              noun={noun}
            />
          </>
        )}
      </DataTableCard>

      {footnote && <p className="-mt-2 text-xs text-muted-foreground">{footnote}</p>}
    </div>
  );
}
