import { ChevronLeft, ChevronRight, Search, Smartphone, Users } from "lucide-react";
import { useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableCell, TableHead, TableRow } from "@/components/ui/table";
import { cn } from "@/lib/utils";

type Membership = { expires: string | null };

export type ManagerUser = {
  id: number;
  name: string;
  initials: string;
  email: string;
  phone: string;
  joined: string;
  devices: number;
  membership: Membership | null;
};

type Props = {
  users: ManagerUser[];
  detailUrl: string; // ".../users/0/" con el 0 de marcador
};

type Filter = "all" | "active" | "inactive";

const PAGE_SIZE = 20;

export default function UsersTable({ users, detailUrl }: Props) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<Filter>("all");
  const [page, setPage] = useState(1);

  const counts = useMemo(
    () => ({
      all: users.length,
      active: users.filter((u) => u.membership).length,
      inactive: users.filter((u) => !u.membership).length,
    }),
    [users],
  );

  const matches = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return users.filter((user) => {
      if (filter === "active" && !user.membership) return false;
      if (filter === "inactive" && user.membership) return false;
      if (!needle) return true;
      return (
        user.name.toLowerCase().includes(needle) ||
        user.email.toLowerCase().includes(needle) ||
        user.phone.toLowerCase().includes(needle)
      );
    });
  }, [users, query, filter]);

  const pages = Math.max(1, Math.ceil(matches.length / PAGE_SIZE));
  const current = Math.min(page, pages);
  const visible = matches.slice((current - 1) * PAGE_SIZE, current * PAGE_SIZE);

  function change(next: Partial<{ query: string; filter: Filter }>) {
    if (next.query !== undefined) setQuery(next.query);
    if (next.filter !== undefined) setFilter(next.filter);
    setPage(1);
  }

  const tabs: { key: Filter; label: string }[] = [
    { key: "all", label: "Todos" },
    { key: "active", label: "Con membresía" },
    { key: "inactive", label: "Sin membresía" },
  ];

  return (
    <div className="rounded-lg border border-border bg-background">
      <div className="flex flex-wrap items-center gap-4 border-b border-border px-6 py-5">
        <div className="relative w-full max-w-xs">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(event) => change({ query: event.target.value })}
            placeholder="Buscar por nombre, email o teléfono..."
            className="pl-9"
            aria-label="Buscar usuarios"
          />
        </div>

        <div className="flex gap-1 rounded-lg bg-muted p-1">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              type="button"
              onClick={() => change({ filter: tab.key })}
              className={cn(
                "flex items-center gap-1.5 rounded-md px-3 py-1.5 text-[0.8125rem] font-medium transition-colors",
                filter === tab.key
                  ? "bg-background text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              {tab.label}
              <span
                className={cn(
                  "rounded-full px-1.5 py-0.5 text-[0.6875rem]",
                  filter === tab.key
                    ? "bg-primary text-primary-foreground"
                    : "bg-border text-muted-foreground",
                )}
              >
                {counts[tab.key]}
              </span>
            </button>
          ))}
        </div>

        <span className="ml-auto text-xs text-muted-foreground">
          {matches.length} {matches.length === 1 ? "resultado" : "resultados"}
        </span>
      </div>

      {visible.length === 0 ? (
        <div className="px-8 py-16 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted text-muted-foreground">
            <Users className="h-6 w-6" />
          </div>
          <h5 className="mb-2 text-base font-semibold text-foreground">
            No se encontraron usuarios
          </h5>
          <p className="text-sm text-muted-foreground">
            {query ? `No hay resultados para "${query}"` : "No hay usuarios en este filtro"}
          </p>
        </div>
      ) : (
        <>
          <Table>
            <thead>
              <tr>
                <TableHead>Usuario</TableHead>
                <TableHead>Teléfono</TableHead>
                <TableHead>Membresía</TableHead>
                <TableHead>Dispositivos</TableHead>
                <TableHead>Registro</TableHead>
                <TableHead className="text-right">Acciones</TableHead>
              </tr>
            </thead>
            <tbody>
              {visible.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <div
                        className={cn(
                          "flex h-10 w-10 flex-none items-center justify-center rounded-full text-sm font-semibold",
                          user.membership
                            ? "bg-emerald-500 text-white"
                            : "bg-muted text-muted-foreground",
                        )}
                      >
                        {user.initials}
                      </div>
                      <div className="min-w-0">
                        <div className="truncate text-sm font-medium text-foreground">
                          {user.name}
                        </div>
                        <div className="truncate text-xs text-muted-foreground">{user.email}</div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="text-sm">{user.phone}</TableCell>
                  <TableCell>
                    {user.membership ? (
                      <>
                        <Badge variant="success">Activa</Badge>
                        {user.membership.expires && (
                          <div className="mt-1 text-[0.6875rem] text-muted-foreground">
                            Vence: {user.membership.expires}
                          </div>
                        )}
                      </>
                    ) : (
                      <Badge variant="neutral">Sin membresía</Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    {user.devices > 0 ? (
                      <span className="inline-flex items-center gap-1 rounded border border-border bg-muted px-2 py-0.5 text-[0.6875rem] font-medium text-muted-foreground">
                        <Smartphone className="h-3 w-3" />
                        {user.devices}
                      </span>
                    ) : (
                      <span className="text-xs text-muted-foreground">—</span>
                    )}
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">{user.joined}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="outline" size="sm" asChild>
                      <a href={detailUrl.replace("/0/", `/${user.id}/`)}>Ver detalle</a>
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </tbody>
          </Table>

          {pages > 1 && (
            <div className="flex items-center justify-center gap-2 px-6 py-4">
              <Button
                variant="outline"
                size="icon"
                onClick={() => setPage(current - 1)}
                disabled={current === 1}
                aria-label="Página anterior"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <span className="px-2 text-sm text-muted-foreground">
                {current} de {pages}
              </span>
              <Button
                variant="outline"
                size="icon"
                onClick={() => setPage(current + 1)}
                disabled={current === pages}
                aria-label="Página siguiente"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
