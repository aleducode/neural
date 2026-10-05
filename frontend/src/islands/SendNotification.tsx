import { Check, ChevronsUpDown, Search, Send } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

type Candidate = { id: number; name: string; initials: string; email: string };

type Props = {
  users: Candidate[];
  types: { value: string; label: string }[];
  /** Cuando se entra desde el detalle de un socio, ya viene elegido. */
  lockedUser: Candidate | null;
  defaultType: string;
  cancelUrl: string;
  csrfToken: string;
};

export default function SendNotification({
  users,
  types,
  lockedUser,
  defaultType,
  cancelUrl,
  csrfToken,
}: Props) {
  const [selected, setSelected] = useState<Candidate | null>(lockedUser);
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [type, setType] = useState(defaultType);

  const box = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function onClickOutside(event: MouseEvent) {
      if (box.current && !box.current.contains(event.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, [open]);

  const matches = useMemo(() => {
    const needle = search.trim().toLowerCase();
    if (!needle) return users.slice(0, 50);
    return users
      .filter(
        (user) =>
          user.name.toLowerCase().includes(needle) ||
          user.email.toLowerCase().includes(needle),
      )
      .slice(0, 50);
  }, [users, search]);

  const ready = Boolean(selected && title.trim() && body.trim());

  return (
    <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <form method="post" className="rounded-lg border border-border bg-background">
        <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
        <input type="hidden" name="user" value={selected?.id ?? ""} />
        <input type="hidden" name="notification_type" value={type} />

        <div className="border-b border-border px-6 py-5">
          <h2 className="text-base font-semibold text-foreground">
            Detalles de la notificación
          </h2>
        </div>

        <div className="space-y-5 p-6">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-foreground">
              Usuario *
            </label>

            {lockedUser ? (
              <div className="flex items-center gap-3 rounded-md border border-border bg-secondary p-3">
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500 text-sm font-semibold text-white">
                  {lockedUser.initials}
                </span>
                <div className="min-w-0">
                  <div className="truncate text-sm font-medium">{lockedUser.name}</div>
                  <div className="truncate text-xs text-muted-foreground">
                    {lockedUser.email}
                  </div>
                </div>
              </div>
            ) : (
              <div className="relative" ref={box}>
                <button
                  type="button"
                  onClick={() => setOpen(!open)}
                  className="flex h-9 w-full items-center justify-between rounded-md border border-input bg-background px-3 text-sm"
                  aria-haspopup="listbox"
                  aria-expanded={open}
                >
                  <span className={cn(!selected && "text-muted-foreground")}>
                    {selected ? `${selected.name} (${selected.email})` : "Buscar usuario..."}
                  </span>
                  <ChevronsUpDown className="h-4 w-4 opacity-50" />
                </button>

                {open && (
                  <div className="absolute z-20 mt-1 w-full rounded-md border border-border bg-background shadow-lg">
                    <div className="relative border-b border-border p-2">
                      <Search className="pointer-events-none absolute left-5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        autoFocus
                        value={search}
                        onChange={(event) => setSearch(event.target.value)}
                        placeholder="Nombre o email..."
                        className="h-8 pl-8"
                      />
                    </div>
                    <ul className="max-h-64 overflow-y-auto py-1" role="listbox">
                      {matches.length === 0 && (
                        <li className="px-3 py-6 text-center text-sm text-muted-foreground">
                          No se encontraron usuarios
                        </li>
                      )}
                      {matches.map((user) => (
                        <li key={user.id}>
                          <button
                            type="button"
                            role="option"
                            aria-selected={selected?.id === user.id}
                            onClick={() => {
                              setSelected(user);
                              setOpen(false);
                              setSearch("");
                            }}
                            className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm hover:bg-secondary"
                          >
                            <Check
                              className={cn(
                                "h-4 w-4 flex-none",
                                selected?.id === user.id ? "opacity-100" : "opacity-0",
                              )}
                            />
                            <span className="min-w-0">
                              <span className="block truncate font-medium">{user.name}</span>
                              <span className="block truncate text-xs text-muted-foreground">
                                {user.email}
                              </span>
                            </span>
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                <p className="mt-1.5 text-xs text-muted-foreground">
                  Solo usuarios con dispositivos registrados ({users.length})
                </p>
              </div>
            )}
          </div>

          <div>
            <label htmlFor="title" className="mb-1.5 block text-sm font-medium text-foreground">
              Título *
            </label>
            <Input
              id="title"
              name="title"
              value={title}
              maxLength={200}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="Título de la notificación"
            />
            <p className="mt-1.5 text-xs text-muted-foreground">{title.length}/200</p>
          </div>

          <div>
            <label htmlFor="body" className="mb-1.5 block text-sm font-medium text-foreground">
              Mensaje *
            </label>
            <textarea
              id="body"
              name="body"
              rows={4}
              value={body}
              onChange={(event) => setBody(event.target.value)}
              placeholder="Escribe el mensaje de la notificación..."
              className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            />
          </div>

          <div>
            <label htmlFor="type" className="mb-1.5 block text-sm font-medium text-foreground">
              Tipo de notificación
            </label>
            <select
              id="type"
              value={type}
              onChange={(event) => setType(event.target.value)}
              className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm text-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              {types.map((choice) => (
                <option key={choice.value} value={choice.value}>
                  {choice.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex gap-3 pt-2">
            <Button type="submit" disabled={!ready}>
              <Send className="h-4 w-4" />
              Enviar notificación
            </Button>
            <Button variant="outline" asChild>
              <a href={cancelUrl}>Cancelar</a>
            </Button>
          </div>
        </div>
      </form>

      <div className="h-fit rounded-lg border border-border bg-background">
        <div className="border-b border-border px-6 py-5">
          <h2 className="text-base font-semibold text-foreground">Vista previa</h2>
        </div>
        <div className="p-6">
          <div className="rounded-xl border border-border bg-muted p-4">
            <div className="rounded-lg bg-background p-3 shadow-sm">
              <div className="flex items-start gap-3">
                <span className="flex h-8 w-8 flex-none items-center justify-center rounded-lg bg-emerald-500 text-xs font-bold text-white">
                  N
                </span>
                <div className="min-w-0 flex-1">
                  <div className="mb-0.5 text-[0.6875rem] text-muted-foreground">NEURAL</div>
                  <div className="mb-1 break-words text-[0.8125rem] font-semibold text-foreground">
                    {title || "Título de la notificación"}
                  </div>
                  <div className="break-words text-xs leading-relaxed text-muted-foreground">
                    {body || "El mensaje de la notificación aparecerá aquí..."}
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-3 text-center text-[0.6875rem] text-muted-foreground">Ahora</div>
          </div>

          <ul className="mt-4 space-y-1 border-t border-border pt-4 text-xs text-muted-foreground">
            <li>La notificación se enviará inmediatamente</li>
            <li>El usuario debe tener un dispositivo registrado</li>
            <li>Se enviará a todos los dispositivos activos del usuario</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
