import type { ReactNode } from "react";

/**
 * Cabecera de pantalla del diseño (nodo «Header» #NN1F7): titulo 24/600,
 * bajada 16/400 en secundario y los botones de accion a la derecha.
 */
export function PageHeader({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children?: ReactNode;
}) {
  return (
    <header className="flex flex-wrap items-center justify-between gap-4">
      <div className="min-w-0">
        <h1 className="text-2xl font-semibold text-foreground">{title}</h1>
        <p className="text-base text-muted-foreground">{description}</p>
      </div>
      {children && <div className="flex flex-wrap items-center gap-2">{children}</div>}
    </header>
  );
}
