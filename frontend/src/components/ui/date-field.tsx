import { format, parse } from "date-fns";
import { es } from "date-fns/locale";
import { CalendarIcon } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Field } from "@/components/ui/detail";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";

/**
 * Selector de fecha del panel.
 *
 * El valor viaja en un <input type="hidden"> en ISO, que es lo que el DateField
 * de Django parsea sin ambigüedad. Lo que se ve es el formato colombiano. Un
 * <input type="date"> nativo mostraba «dd/mm/yyyy» en inglés y cambiaba de
 * aspecto en cada navegador.
 */
export function DateField({
  name,
  label,
  defaultValue,
  error,
  fromYear = 1930,
}: {
  name: string;
  label: string;
  /** ISO (YYYY-MM-DD) o vacío. */
  defaultValue?: string;
  error?: string;
  fromYear?: number;
}) {
  const [value, setValue] = useState<Date | undefined>(() => {
    if (!defaultValue) return undefined;
    const parsed = parse(defaultValue, "yyyy-MM-dd", new Date());
    return Number.isNaN(parsed.getTime()) ? undefined : parsed;
  });
  const [open, setOpen] = useState(false);
  const today = new Date();

  return (
    <Field name={name} label={label} error={error}>
      <input type="hidden" name={name} value={value ? format(value, "yyyy-MM-dd") : ""} />
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            type="button"
            id={name}
            variant="outline"
            aria-invalid={error ? true : undefined}
            className={cn(
              "h-10 w-full justify-start rounded-md px-3 font-normal",
              !value && "text-muted-foreground",
            )}
          >
            <CalendarIcon className="text-faint" />
            {value ? format(value, "d 'de' MMMM 'de' yyyy", { locale: es }) : "Sin fecha"}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            mode="single"
            locale={es}
            selected={value}
            defaultMonth={value ?? new Date(today.getFullYear() - 25, 0)}
            captionLayout="dropdown"
            startMonth={new Date(fromYear, 0)}
            endMonth={today}
            disabled={{ after: today }}
            onSelect={(date) => {
              setValue(date);
              setOpen(false);
            }}
          />
          {value && (
            <div className="border-t border-border p-2">
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="w-full"
                onClick={() => {
                  setValue(undefined);
                  setOpen(false);
                }}
              >
                Borrar fecha
              </Button>
            </div>
          )}
        </PopoverContent>
      </Popover>
    </Field>
  );
}
