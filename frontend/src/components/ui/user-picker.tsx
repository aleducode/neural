import { Check, ChevronsUpDown, X } from "lucide-react";
import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Field } from "@/components/ui/detail";
import { MemberAvatar } from "@/components/ui/member-avatar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";

/**
 * Elegir usuarios por nombre, uno o varios.
 *
 * Los seleccionados viajan como varios <input name="users"> ocultos, que es lo
 * que Django lee con getlist: el formulario sigue funcionando sin JavaScript si
 * la isla no monta.
 *
 * La lista llega entera en las props y se busca en el cliente. Con ~740 usuarios
 * son unos 70 KB y la búsqueda es instantánea; pedirle al servidor en cada tecla
 * sería más lento y más frágil.
 */

export type PickerUser = {
  id: number;
  name: string;
  email: string;
  initials: string;
  photo: string | null;
};

export function UserPicker({
  name,
  label,
  users,
  error,
  placeholder = "Buscar por nombre o email…",
}: {
  name: string;
  label: string;
  users: PickerUser[];
  error?: string;
  placeholder?: string;
}) {
  const [elegidos, setElegidos] = useState<PickerUser[]>([]);
  const [abierto, setAbierto] = useState(false);

  const porId = useMemo(() => new Set(elegidos.map((u) => u.id)), [elegidos]);

  const alternar = (user: PickerUser) =>
    setElegidos((actuales) =>
      actuales.some((u) => u.id === user.id)
        ? actuales.filter((u) => u.id !== user.id)
        : [...actuales, user],
    );

  return (
    <Field name={name} label={label} error={error}>
      {elegidos.map((user) => (
        <input key={user.id} type="hidden" name={name} value={user.id} />
      ))}

      <Popover open={abierto} onOpenChange={setAbierto}>
        <PopoverTrigger asChild>
          <Button
            type="button"
            variant="outline"
            role="combobox"
            aria-expanded={abierto}
            className="h-10 w-full justify-between rounded-md px-3 font-normal"
          >
            <span className={cn("truncate", !elegidos.length && "text-muted-foreground")}>
              {elegidos.length === 0
                ? "Elegí uno o varios usuarios"
                : `${elegidos.length} usuario${elegidos.length === 1 ? "" : "s"} elegido${elegidos.length === 1 ? "" : "s"}`}
            </span>
            <ChevronsUpDown className="ml-2 size-4 shrink-0 text-faint" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[--radix-popover-trigger-width] p-0" align="start">
          <Command
            filter={(value, search) =>
              value.toLowerCase().includes(search.toLowerCase()) ? 1 : 0
            }
          >
            <CommandInput placeholder={placeholder} />
            <CommandList>
              <CommandEmpty>Ningún usuario coincide.</CommandEmpty>
              <CommandGroup>
                {users.map((user) => (
                  <CommandItem
                    key={user.id}
                    value={`${user.name} ${user.email}`}
                    onSelect={() => alternar(user)}
                    className="gap-2.5"
                  >
                    <MemberAvatar
                      name={user.name}
                      initials={user.initials}
                      photo={user.photo}
                      className="size-7"
                    />
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm text-foreground">
                        {user.name}
                      </span>
                      <span className="block truncate text-xs text-muted-foreground">
                        {user.email}
                      </span>
                    </span>
                    <Check
                      className={cn(
                        "size-4 text-primary",
                        porId.has(user.id) ? "opacity-100" : "opacity-0",
                      )}
                    />
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>

      {elegidos.length > 0 && (
        <ul className="flex flex-wrap gap-1.5">
          {elegidos.map((user) => (
            <li key={user.id}>
              <button
                type="button"
                onClick={() => alternar(user)}
                className="flex items-center gap-1.5 rounded-full bg-accent py-0.5 pl-1 pr-2 text-xs font-medium text-foreground hover:bg-border"
                aria-label={`Quitar ${user.name}`}
              >
                <MemberAvatar
                  name={user.name}
                  initials={user.initials}
                  photo={user.photo}
                  className="size-5"
                  fallbackClassName="text-[0.5rem]"
                />
                <span className="max-w-32 truncate">{user.name}</span>
                <X className="size-3 text-muted-foreground" aria-hidden="true" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </Field>
  );
}
