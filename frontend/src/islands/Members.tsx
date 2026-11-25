import { useMemo, useState } from "react";

import { BellPlus, Check, UserPlus, Users, X } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { SelectField, TextField } from "@/components/ui/detail";
import { Dialog, DialogClose, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog";
import { ListSection } from "@/components/ui/list-section";
import { PersonCell } from "@/components/ui/person-cell";
import { type Kpi } from "@/components/ui/stat-widget";
import { TableCell } from "@/components/ui/table";
import { cn } from "@/lib/utils";

type Tone = "success" | "warning" | "error" | "neutral";
type Account = "ok" | "pending" | "inactive";

type Member = {
  no: number;
  id: number;
  name: string;
  initials: string;
  photo: string | null;
  email: string;
  phone: string;
  plan: string;
  status: string;
  tone: Tone;
  joined: string | null;
  expires: string | null;
  lastCheckin: string;
  account: Account;
};

type Plan = { value: string; label: string; days: number; sessions: number; price: string | null; priceRaw: number };
type Errors = Record<string, { message: string }[]>;

type Props = {
  kpis: Kpi[];
  rows: Member[];
  userDetailUrl: string;
  sendUrl: string;
  planChoices: Plan[];
  csrfToken: string;
  errors?: Errors;
  values?: Record<string, string>;
};

const FILTERS: { key: "all" | Account; label: string }[] = [
  { key: "all", label: "Todos" },
  { key: "pending", label: "Por aprobar" },
  { key: "inactive", label: "Desactivados" },
];

export default function Members({ kpis, rows, userDetailUrl, sendUrl, planChoices, csrfToken, errors, values }: Props) {
  const hasErrors = Boolean(errors && Object.keys(errors).length);
  const [creating, setCreating] = useState(hasErrors);
  const [filter, setFilter] = useState<"all" | Account>("all");

  const counts = useMemo(
    () => ({
      all: rows.length,
      ok: rows.filter((r) => r.account === "ok").length,
      pending: rows.filter((r) => r.account === "pending").length,
      inactive: rows.filter((r) => r.account === "inactive").length,
    }),
    [rows],
  );
  const visible = filter === "all" ? rows : rows.filter((r) => r.account === filter);

  return (
    <>
      <ListSection<Member>
        title="Usuarios"
        description="Todos los usuarios del gimnasio, su membresía y su actividad."
        actions={
          <div className="flex flex-wrap gap-2">
            <Button size="sm" variant="outline" asChild>
              <a href={sendUrl}>
                <BellPlus />
                Enviar notificación
              </a>
            </Button>
            <Button size="sm" onClick={() => setCreating(true)}>
              <UserPlus />
              Agregar usuario
            </Button>
          </div>
        }
        kpis={kpis}
        tableIcon={<Users className="size-5" />}
        tableTitle="Listado de usuarios"
        tableActions={
          <div role="tablist" aria-label="Filtrar por estado de la cuenta" className="flex gap-1 rounded-lg bg-accent p-1">
              {FILTERS.map((f) => (
                <button
                  key={f.key}
                  type="button"
                  role="tab"
                  aria-selected={filter === f.key}
                  onClick={() => setFilter(f.key)}
                  className={cn(
                    "flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-medium text-muted-foreground transition-colors hover:text-foreground",
                    filter === f.key && "bg-background text-foreground shadow-sm",
                  )}
                >
                  {f.label}
                  <span className="tabular-nums">{counts[f.key]}</span>
                </button>
              ))}
            </div>
        }
        searchPlaceholder="Buscar por nombre, email o teléfono"
        haystack={(row) => `${row.name} ${row.email} ${row.phone} ${row.plan}`}
        rows={visible}
        rowKey={(row) => row.id}
        noun="usuarios"
        minWidth="920px"
        columns={[
          { label: "No", className: "w-16" },
          { label: "Usuario" },
          { label: "Plan" },
          { label: "Estado" },
          { label: "Registro" },
          { label: "Vence" },
          { label: "Último check-in" },
        ]}
        emptyIcon={<Users />}
        emptyTitle={filter === "pending" ? "Nadie por aprobar" : filter === "inactive" ? "Ninguna cuenta desactivada" : "Sin usuarios"}
        emptyDetail={
          filter === "pending"
            ? "Quien se registre desde la app aparece acá hasta que lo aprueben."
            : filter === "inactive"
              ? "Las cuentas desactivadas desde la ficha del usuario aparecen acá."
              : "Todavía no hay nadie registrado como usuario."
        }
        renderRow={(row, index) => (
          <>
            <TableCell className="text-sm tabular-nums text-muted-foreground">{index}</TableCell>
            <PersonCell
              name={row.name}
              initials={row.initials}
              photo={row.photo}
              sub={row.email}
              href={userDetailUrl.replace("/0/", `/${row.id}/`)}
            />
            <TableCell className="whitespace-nowrap text-sm text-foreground">{row.plan}</TableCell>
            <TableCell>
              <div className="flex flex-wrap gap-1.5">
                {row.account === "inactive" ? (
                  <Badge dot variant="error">Desactivada</Badge>
                ) : (
                  <>
                    {row.account === "pending" && <Badge dot variant="warning">Por aprobar</Badge>}
                    <Badge dot variant={row.tone}>{row.status}</Badge>
                  </>
                )}
              </div>
            </TableCell>
            <TableCell className="whitespace-nowrap text-sm text-muted-foreground">{row.joined ?? "—"}</TableCell>
            <TableCell className="whitespace-nowrap text-sm text-muted-foreground">{row.expires ?? "—"}</TableCell>
            <TableCell className="whitespace-nowrap text-sm text-muted-foreground">{row.lastCheckin}</TableCell>
          </>
        )}
      />

      <AddMember
        open={creating}
        onClose={() => setCreating(false)}
        plans={planChoices}
        csrfToken={csrfToken}
        errors={errors}
        values={values}
      />
    </>
  );
}

const PERSONAL_FIELDS = ["first_name", "last_name", "email", "phone_number", "birthdate", "__all__"];

/**
 * «15. Member - Add New Member». The design has four steps; Neural only has
 * data for two of them --who the person is and their plan--, so «Gym
 * Information» and «Notes» are not drawn: they would be inputs that save
 * nowhere.
 *
 * Both steps live in one <form>: the second is hidden, not unmounted, so a
 * plain submit sends everything and the server validates it together.
 */
function AddMember({
  open,
  onClose,
  plans,
  csrfToken,
  errors,
  values,
}: {
  open: boolean;
  onClose: () => void;
  plans: Plan[];
  csrfToken: string;
  errors?: Errors;
  values?: Record<string, string>;
}) {
  const err = (field: string) => errors?.[field]?.[0]?.message;
  const personalFailed = PERSONAL_FIELDS.some((f) => err(f));
  const planFailed = Boolean(errors && !personalFailed && Object.keys(errors).length);

  const [step, setStep] = useState(planFailed ? 2 : 1);
  const [withPlan, setWithPlan] = useState(values?.with_plan === "on");
  const [planId, setPlanId] = useState(values?.plan || plans[0]?.value || "");
  const [from, setFrom] = useState(values?.init_date || new Date().toISOString().slice(0, 10));
  const [charge, setCharge] = useState(values ? values.charge === "on" : true);
  const plan = plans.find((p) => p.value === planId);

  const expires = (() => {
    if (!plan || !from) return null;
    const d = new Date(`${from}T00:00:00`);
    if (Number.isNaN(d.getTime())) return null;
    d.setDate(d.getDate() + plan.days);
    return d.toLocaleDateString("es-CO", { day: "numeric", month: "long", year: "numeric" });
  })();

  const goNext = (form: HTMLFormElement | null) => {
    // The browser checks the required fields of step one before moving on,
    // so the error shows where the person is looking.
    const inputs = Array.from(form?.querySelectorAll<HTMLInputElement>("[data-step='1'] input") ?? []);
    const invalid = inputs.find((input) => !input.checkValidity());
    if (invalid) {
      invalid.reportValidity();
      return;
    }
    setStep(2);
  };

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="max-h-[calc(100dvh-2rem)] max-w-[700px] gap-0 overflow-y-auto rounded-2xl p-0 [&>button:last-child]:hidden">
        <header className="flex items-center justify-between gap-2 border-b border-border bg-secondary p-6">
          <div>
            <DialogTitle className="text-lg font-semibold">Agregar usuario</DialogTitle>
            <DialogDescription className="sr-only">
              Crea la cuenta y le manda al usuario un correo para que elija su contraseña.
            </DialogDescription>
          </div>
          <DialogClose asChild>
            <Button variant="outline" size="icon" className="size-10 rounded-full" aria-label="Cerrar">
              <X />
            </Button>
          </DialogClose>
        </header>

        <ol className="flex flex-wrap items-center gap-4 border-b border-border p-6">
          {[
            { n: 1, label: "Datos personales" },
            { n: 2, label: "Membresía" },
          ].map((s, i) => (
            <li key={s.n} className="flex items-center gap-4">
              {i > 0 && <span aria-hidden className="h-px w-8 bg-border" />}
              <button
                type="button"
                onClick={() => (s.n === 1 ? setStep(1) : goNext(document.getElementById("add-member") as HTMLFormElement))}
                aria-current={step === s.n ? "step" : undefined}
                className="flex items-center gap-2.5 text-sm font-medium"
              >
                <span
                  className={cn(
                    "flex size-6 items-center justify-center rounded-full text-sm text-white",
                    step === s.n ? "bg-positive" : step > s.n ? "bg-positive/70" : "bg-border",
                  )}
                >
                  {step > s.n ? <Check className="size-3.5" /> : s.n}
                </span>
                <span className={step === s.n ? "text-foreground" : "text-muted-foreground"}>{s.label}</span>
              </button>
            </li>
          ))}
        </ol>

        <form id="add-member" method="post" className="flex flex-col" noValidate={false}>
          <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />

          <section data-step="1" className={cn("flex-col gap-4 p-6", step === 1 ? "flex" : "hidden")}>
            <h3 className="text-base font-semibold text-foreground">Datos personales</h3>
            {err("__all__") && (
              <p role="alert" className="text-sm text-destructive">{err("__all__")}</p>
            )}
            <div className="flex flex-col gap-4 sm:flex-row">
              <TextField name="first_name" label="Nombres *" defaultValue={values?.first_name} error={err("first_name")} required autoComplete="off" />
              <TextField name="last_name" label="Apellidos *" defaultValue={values?.last_name} error={err("last_name")} required autoComplete="off" />
            </div>
            <TextField
              name="email"
              label="Correo *"
              type="email"
              defaultValue={values?.email}
              error={err("email")}
              hint="Con este correo entra a la app. Le llega ahí el enlace para elegir su contraseña."
              required
              autoComplete="off"
            />
            <TextField
              name="phone_number"
              label="Teléfono"
              type="tel"
              inputMode="tel"
              defaultValue={values?.phone_number}
              error={err("phone_number")}
              hint="Celular, solo números. Por ejemplo 3001234567."
              autoComplete="off"
            />
            <TextField name="birthdate" label="Fecha de nacimiento" type="date" defaultValue={values?.birthdate} error={err("birthdate")} />
          </section>

          <section data-step="2" className={cn("flex-col gap-4 p-6", step === 2 ? "flex" : "hidden")}>
            <h3 className="text-base font-semibold text-foreground">Membresía</h3>
            <label className="flex items-center gap-2 text-sm text-foreground">
              <input
                type="checkbox"
                name="with_plan"
                checked={withPlan}
                onChange={(e) => setWithPlan(e.target.checked)}
                className="size-4 rounded-sm border-border accent-[hsl(var(--primary))]"
              />
              Activarle un plan ahora
            </label>
            {!withPlan && (
              <p className="text-sm text-muted-foreground">
                La cuenta queda sin plan. Se lo podés activar después desde su ficha, o lo paga él desde la app.
              </p>
            )}
            {withPlan && plans.length === 0 && (
              <p className="text-sm text-muted-foreground">No hay planes creados. Crealos primero en «Planes».</p>
            )}
            {withPlan && plans.length > 0 && (
              <>
                <SelectField
                  name="plan"
                  label="Plan"
                  defaultValue={planId}
                  onChange={setPlanId}
                  error={err("plan")}
                  options={plans.map((p) => ({
                    value: p.value,
                    label: p.sessions ? `${p.label} — ${p.sessions} sesiones` : p.label,
                  }))}
                />
                <TextField
                  name="init_date"
                  label="Desde"
                  type="date"
                  defaultValue={from}
                  error={err("init_date")}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFrom(e.target.value)}
                />
                <label className="flex items-center gap-2 text-sm text-muted-foreground">
                  <input
                    type="checkbox"
                    name="charge"
                    checked={charge}
                    onChange={(e) => setCharge(e.target.checked)}
                    className="size-4 rounded-sm border-border accent-[hsl(var(--primary))]"
                  />
                  Registrar el cobro
                </label>
                {charge && (
                  <TextField
                    key={planId}
                    name="amount"
                    label="Monto cobrado"
                    type="number"
                    min={0}
                    step={1000}
                    defaultValue={(planId === values?.plan && values?.amount) || plan?.priceRaw || 0}
                    error={err("amount")}
                    hint="Editalo si hubo descuento. En cero queda como cortesía."
                  />
                )}
                {plan && expires && (
                  <p className="rounded-md border border-border bg-secondary px-3 py-2 text-xs text-muted-foreground">
                    Vence el <span className="font-medium text-foreground">{expires}</span> ({plan.days} días)
                    {plan.sessions > 0 && (
                      <>
                        {" · "}
                        <span className="font-medium text-foreground">{plan.sessions} sesiones</span> para agendar
                      </>
                    )}
                  </p>
                )}
              </>
            )}
          </section>

          <footer className="flex flex-wrap items-center justify-end gap-3.5 border-t border-border px-6 py-5">
            {step === 1 ? (
              <>
                <DialogClose asChild>
                  <Button type="button" variant="outline" className="h-12 rounded-[10px] px-4 text-base font-semibold">
                    Cancelar
                  </Button>
                </DialogClose>
                {/* Keyed so React does not reuse this node as the submit
                    button of step two mid-click, which submitted the form. */}
                <Button
                  key="next"
                  type="button"
                  className="h-12 rounded-[10px] px-4 text-base font-semibold"
                  onClick={(e) => {
                    e.preventDefault();
                    goNext(e.currentTarget.form);
                  }}
                >
                  Siguiente
                </Button>
              </>
            ) : (
              <>
                <Button key="back" type="button" variant="outline" className="h-12 rounded-[10px] px-4 text-base font-semibold" onClick={() => setStep(1)}>
                  Atrás
                </Button>
                <Button key="submit" type="submit" className="h-12 rounded-[10px] px-4 text-base font-semibold">
                  Crear cuenta
                </Button>
              </>
            )}
          </footer>
        </form>
      </DialogContent>
    </Dialog>
  );
}
