import { useState, type ReactNode } from "react";

import {
  ArrowLeft,
  BadgeCheck,
  BellPlus,
  CalendarCheck,
  CalendarDays,
  ClipboardList,
  CreditCard,
  Mail,
  Phone,
  Library,
  Scale,
  Smartphone,
} from "lucide-react";

import { MemberAvatar } from "@/components/ui/member-avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DateField } from "@/components/ui/date-field";
import {
  DetailHero,
  FormFooter,
  KeyValue,
  SelectField,
  TextField,
  WeekBars,
  type Tone,
} from "@/components/ui/detail";
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty";
import { StatWidget, type Kpi } from "@/components/ui/stat-widget";
import { Table, TableCell, TableHead, TableRow } from "@/components/ui/table";
import { ProgressBar } from "@/components/ui/progress-bar";
import { VideoThumb } from "@/components/ui/video-thumb";
import { Widget, WidgetHeader } from "@/components/ui/widget";

type Errors = Record<string, { message: string }[]>;

type Props = {
  member: {
    id: number;
    name: string;
    initials: string;
    photo: string | null;
    email: string;
    phone: string;
    verified: boolean;
    joined: string | null;
    status: string;
    tone: Tone;
  };
  kpis: Kpi[];
  form: Record<string, string | number | boolean>;
  age: string | null;
  planChoices: { value: string; label: string; days: number; sessions: number; price: string | null }[];
  membership: {
    isTicketPack: boolean;
    sessionsTotal: number;
    sessionsUsed: number;
    sessionsLeft: number | null;
    plan: string | null;
    type: string | null;
    price: string | null;
    duration: string | null;
    start: string | null;
    end: string | null;
    daysLeft: number | null;
    elapsed: number | null;
    total: number | null;
    status: string;
    tone: Tone;
  };
  weekly: { label: string; value: number }[];
  weeklyTotal: number;
  activity: { id: number; date: string | null; klass: string; time: string; status: string; tone: Tone }[];
  payments: { id: number; reference: string; plan: string; amount: string; date: string; paid: boolean; status: string }[];
  weights: { id: number; date: string | null; weight: string; delta: string | null; up: boolean }[];
  devices: { id: number; platform: string; deviceId: string; active: boolean; seen: string | null }[];
  videoPackages: {
    id: number;
    name: string;
    cover: string | null;
    kind: string;
    videos: number;
    done: number;
    percent: number;
    items: {
      id: number;
      name: string;
      poster: string | null;
      duration: string;
      watched: string | null;
      percent: number;
      completed: boolean;
      lastSeen: string | null;
    }[];
  }[];
  packageDetailUrl: string;
  errors?: Errors;
  csrfToken: string;
  backUrl: string;
  sendUrl: string;
};

const err = (errors: Errors | undefined, field: string) => errors?.[field]?.[0]?.message;

export default function MemberDetail({
  member,
  kpis,
  form,
  age,
  membership,
  planChoices,
  weekly,
  weeklyTotal,
  activity,
  payments,
  weights,
  devices,
  videoPackages,
  packageDetailUrl,
  errors,
  csrfToken,
  backUrl,
  sendUrl,
}: Props) {
  const progress =
    membership.total && membership.elapsed !== null
      ? Math.min(Math.round((membership.elapsed / membership.total) * 100), 100)
      : null;

  return (
    <div className="flex flex-col gap-6">
      <Button variant="ghost" size="sm" className="-ml-2 self-start" asChild>
        <a href={backUrl}>
          <ArrowLeft />
          Volver a usuarios
        </a>
      </Button>

      <DetailHero
        portrait={
          <MemberAvatar
            name={member.name}
            initials={member.initials}
            photo={member.photo}
            className="size-20"
            fallbackClassName="text-xl"
          />
        }
        title={member.name}
        badges={[
          ...(member.verified ? [{ label: "Verificado", tone: "success" as Tone }] : []),
          { label: member.status, tone: membership.tone },
        ]}
        meta={[
          { icon: Mail, value: member.email },
          { icon: Phone, value: member.phone },
          ...(member.joined ? [{ icon: CalendarDays, value: `Usuario desde ${member.joined}` }] : []),
          ...(age ? [{ icon: BadgeCheck, value: age }] : []),
        ]}
        actions={
          <Button size="sm" asChild>
            <a href={sendUrl}>
              <BellPlus />
              Enviar notificación
            </a>
          </Button>
        }
      />

      <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.map((kpi) => (
          <StatWidget {...kpi} key={kpi.key} />
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_364px] xl:items-start">
        <div className="flex flex-col gap-6">
          <Widget>
            <WidgetHeader icon={<ClipboardList className="size-5" />} title="Ficha del usuario">
              <span className="text-xs text-muted-foreground">Editable por el equipo</span>
            </WidgetHeader>

            {/* Mismo URL que el GET: si la isla no monta, el form sigue enviando. */}
            <form method="post" className="flex flex-col">
              <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />

              <div className="flex flex-col gap-4 p-5">
                {err(errors, "__all__") && (
                  <p role="alert" className="text-sm text-destructive">
                    {err(errors, "__all__")}
                  </p>
                )}
                <div className="flex flex-wrap gap-4">
                  <TextField name="first_name" label="Nombres" defaultValue={String(form.first_name)} error={err(errors, "first_name")} />
                  <TextField name="last_name" label="Apellidos" defaultValue={String(form.last_name)} error={err(errors, "last_name")} />
                </div>
                <div className="flex flex-wrap gap-4">
                  <TextField name="phone_number" label="Teléfono" defaultValue={String(form.phone_number)} error={err(errors, "phone_number")} />
                  <DateField name="birthdate" label="Fecha de nacimiento" defaultValue={String(form.birthdate)} error={err(errors, "birthdate")} />
                </div>
                <div className="flex flex-wrap gap-4">
                  <TextField name="height" label="Altura (cm)" type="number" min={50} max={260} defaultValue={String(form.height)} error={err(errors, "height")} />
                  <TextField name="profession" label="Profesión" defaultValue={String(form.profession)} error={err(errors, "profession")} />
                </div>
                <div className="flex flex-wrap gap-4">
                  <TextField name="instagram" label="Instagram" defaultValue={String(form.instagram)} error={err(errors, "instagram")} />
                  <TextField name="address" label="Dirección" defaultValue={String(form.address)} error={err(errors, "address")} />
                </div>

                <hr className="border-border" />
                <p className="text-xs font-semibold text-foreground">Contacto de emergencia</p>
                <div className="flex flex-wrap gap-4">
                  <TextField name="emergency_contact" label="Nombre" defaultValue={String(form.emergency_contact)} error={err(errors, "emergency_contact")} />
                  <TextField name="emergency_contact_phone" label="Teléfono" defaultValue={String(form.emergency_contact_phone)} error={err(errors, "emergency_contact_phone")} />
                </div>

                <label className="flex items-center gap-2 text-sm text-muted-foreground">
                  <input
                    type="checkbox"
                    name="hide_from_leaderboard"
                    defaultChecked={Boolean(form.hide_from_leaderboard)}
                    className="size-4 rounded-sm border-border accent-[hsl(var(--primary))]"
                  />
                  Ocultar del ranking público
                </label>
              </div>

              <FormFooter hint="El peso y la membresía se editan desde sus propias pantallas, no desde la ficha.">
                <Button type="reset" variant="outline" size="sm">
                  Descartar
                </Button>
                <Button type="submit" size="sm">
                  Guardar cambios
                </Button>
              </FormFooter>
            </form>
          </Widget>

          <Widget>
            <WidgetHeader icon={<CalendarCheck className="size-5" />} title="Actividad reciente">
              <span className="text-xs text-muted-foreground">Últimas 8 reservas</span>
            </WidgetHeader>
            {activity.length === 0 ? (
              <EmptyCard icon={<CalendarCheck />} title="Sin reservas" detail="Este usuario nunca reservó una clase." />
            ) : (
              <Table>
                <thead>
                  <tr>
                    <TableHead>Fecha</TableHead>
                    <TableHead>Clase</TableHead>
                    <TableHead>Horario</TableHead>
                    <TableHead>Estado</TableHead>
                  </tr>
                </thead>
                <tbody>
                  {activity.map((row) => (
                    <TableRow key={row.id}>
                      <TableCell className="whitespace-nowrap text-sm font-medium text-foreground">{row.date ?? "—"}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">{row.klass}</TableCell>
                      <TableCell className="whitespace-nowrap text-sm tabular-nums text-muted-foreground">{row.time}</TableCell>
                      <TableCell>
                        <Badge dot variant={row.tone}>{row.status}</Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </tbody>
              </Table>
            )}
          </Widget>

          <Widget>
            <WidgetHeader icon={<CreditCard className="size-5" />} title="Pagos" />
            {payments.length === 0 ? (
              <EmptyCard icon={<CreditCard />} title="Sin pagos" detail="No hay ninguna referencia de pago a su nombre." />
            ) : (
              <Table>
                <thead>
                  <tr>
                    <TableHead>Referencia</TableHead>
                    <TableHead>Plan</TableHead>
                    <TableHead>Monto</TableHead>
                    <TableHead>Fecha</TableHead>
                    <TableHead>Estado</TableHead>
                  </tr>
                </thead>
                <tbody>
                  {payments.map((row) => (
                    <TableRow key={row.id}>
                      <TableCell className="whitespace-nowrap text-sm font-medium tabular-nums text-foreground">{row.reference}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">{row.plan}</TableCell>
                      <TableCell className="whitespace-nowrap text-sm font-medium tabular-nums text-foreground">{row.amount}</TableCell>
                      <TableCell className="whitespace-nowrap text-sm text-muted-foreground">{row.date}</TableCell>
                      <TableCell>
                        <Badge dot variant={row.paid ? "success" : "neutral"}>{row.status}</Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </tbody>
              </Table>
            )}
          </Widget>
        </div>

        <div className="flex flex-col gap-6">
          <Widget>
            <WidgetHeader icon={<BadgeCheck className="size-5" />} title="Membresía" />
            {membership.plan ? (
              <div className="flex flex-col gap-4 p-5">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-lg font-semibold text-foreground">{membership.plan}</p>
                    <p className="text-xs text-faint">
                      {[membership.price, membership.duration].filter(Boolean).join(" · ")}
                    </p>
                  </div>
                  <Badge dot variant={membership.tone}>{membership.status}</Badge>
                </div>
                <dl className="flex flex-col gap-2">
                  <KeyValue term="Inicio">{membership.start ?? "—"}</KeyValue>
                  <KeyValue term="Vence">{membership.end ?? "—"}</KeyValue>
                  {membership.isTicketPack && (
                    <KeyValue term="Sesiones">
                      {membership.sessionsLeft} de {membership.sessionsTotal} sin usar
                    </KeyValue>
                  )}
                </dl>

                {membership.isTicketPack && (
                  <div className="flex flex-col gap-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span
                        className={
                          membership.sessionsLeft === 0
                            ? "font-medium text-warning"
                            : "text-muted-foreground"
                        }
                      >
                        {membership.sessionsLeft === 0
                          ? "Ya usó todas sus sesiones"
                          : `${membership.sessionsLeft} ${membership.sessionsLeft === 1 ? "sesión" : "sesiones"} por agendar`}
                      </span>
                      <span className="tabular-nums text-faint">
                        {membership.sessionsUsed} de {membership.sessionsTotal}
                      </span>
                    </div>
                    <div className="h-1.5 overflow-hidden rounded-full bg-accent">
                      <div
                        className={
                          membership.sessionsLeft === 0
                            ? "h-full rounded-full bg-[hsl(var(--warning))]"
                            : "h-full rounded-full bg-primary"
                        }
                        style={{
                          width: `${Math.max(
                            Math.round((membership.sessionsUsed / Math.max(membership.sessionsTotal, 1)) * 100),
                            2,
                          )}%`,
                        }}
                      />
                    </div>
                  </div>
                )}
                {progress !== null && membership.daysLeft !== null && (
                  <div className="flex flex-col gap-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span
                        className={
                          membership.daysLeft <= 7 ? "font-medium text-warning" : "text-muted-foreground"
                        }
                      >
                        {membership.daysLeft < 0
                          ? `Venció hace ${Math.abs(membership.daysLeft)} días`
                          : `Quedan ${membership.daysLeft} días`}
                      </span>
                      <span className="tabular-nums text-faint">
                        {membership.elapsed} de {membership.total}
                      </span>
                    </div>
                    <div className="h-1.5 overflow-hidden rounded-full bg-accent">
                      <div
                        className={
                          membership.daysLeft <= 7
                            ? "h-full rounded-full bg-[hsl(var(--warning))]"
                            : "h-full rounded-full bg-primary"
                        }
                        style={{ width: `${Math.max(progress, 2)}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <EmptyCard icon={<BadgeCheck />} title="Sin membresía activa" detail="No tiene ninguna membresía vigente." />
            )}

            <ActivarPlan planes={planChoices} csrfToken={csrfToken} />
          </Widget>

          <Widget>
            <WidgetHeader icon={<CalendarDays className="size-5" />} title="Entrenamientos">
              <span className="text-xs text-muted-foreground">12 semanas</span>
            </WidgetHeader>
            <div className="flex flex-col gap-3 p-5">
              <p className="flex items-center gap-2">
                <span className="text-2xl font-semibold tabular-nums text-foreground">{weeklyTotal}</span>
                <span className="text-sm text-muted-foreground">sesiones en 12 semanas</span>
              </p>
              <WeekBars points={weekly} />
            </div>
          </Widget>

          <Widget>
            <WidgetHeader icon={<Scale className="size-5" />} title="Peso">
              <span className="text-xs text-muted-foreground">Últimos registros</span>
            </WidgetHeader>
            {weights.length === 0 ? (
              <EmptyCard icon={<Scale />} title="Sin registros" detail="El usuario no ha registrado su peso en la app." />
            ) : (
              <dl className="flex flex-col gap-2.5 p-5">
                {weights.map((row) => (
                  <div key={row.id} className="flex items-center justify-between gap-3">
                    <dt className="text-sm text-muted-foreground">{row.date ?? "—"}</dt>
                    <dd className="flex items-center gap-2">
                      <span className="text-sm font-medium tabular-nums text-foreground">{row.weight}</span>
                      {row.delta && (
                        <span className={row.up ? "text-xs text-destructive" : "text-xs text-positive"}>
                          {row.delta}
                        </span>
                      )}
                    </dd>
                  </div>
                ))}
              </dl>
            )}
          </Widget>

          <Widget>
            <WidgetHeader icon={<Library className="size-5" />} title="Paquetes de video">
              <span className="text-xs text-muted-foreground">
                {videoPackages.length} asignados
              </span>
            </WidgetHeader>
            {videoPackages.length === 0 ? (
              <EmptyCard
                icon={<Library />}
                title="Sin paquetes"
                detail="No tiene ningún paquete de videos asignado."
              />
            ) : (
              <ul className="flex flex-col gap-4 p-5">
                {videoPackages.map((p) => (
                  <li key={p.id} className="flex flex-col gap-2">
                    <a
                      href={packageDetailUrl.replace("/0/", `/${p.id}/`)}
                      className="flex items-center gap-2.5 no-underline"
                    >
                      <VideoThumb poster={p.cover} name={p.name} className="h-9 w-14" />
                      <span className="min-w-0 flex-1">
                        <span className="block truncate text-sm font-medium text-foreground">
                          {p.name}
                        </span>
                        <span className="flex items-center gap-2">
                          <ProgressBar
                            percent={p.percent}
                            done={p.done === p.videos && p.videos > 0}
                            width="w-16"
                          />
                          <span className="text-xs tabular-nums text-faint">
                            {p.done}/{p.videos} vistos
                          </span>
                        </span>
                      </span>
                    </a>

                    {/* Video por video: es lo que el equipo mira para saber
                        dónde se quedó alguien, no solo si empezó. */}
                    <ul className="flex flex-col gap-1.5 border-l border-border pl-3">
                      {p.items.map((v) => (
                        <li key={v.id} className="flex items-center justify-between gap-2">
                          <span className="min-w-0 flex-1">
                            <span className="block truncate text-xs text-foreground">
                              {v.name}
                            </span>
                            <span className="text-[0.625rem] text-faint">
                              {v.completed
                                ? `Terminado · ${v.lastSeen}`
                                : v.watched
                                  ? `${v.watched} de ${v.duration} · ${v.lastSeen}`
                                  : "Sin empezar"}
                            </span>
                          </span>
                          <ProgressBar percent={v.percent} done={v.completed} width="w-12" />
                        </li>
                      ))}
                    </ul>
                  </li>
                ))}
              </ul>
            )}
          </Widget>

          <Widget>
            <WidgetHeader icon={<Smartphone className="size-5" />} title="Dispositivos">
              <span className="text-xs text-muted-foreground">
                {devices.filter((d) => d.active).length} activos
              </span>
            </WidgetHeader>
            {devices.length === 0 ? (
              <EmptyCard icon={<Smartphone />} title="Sin dispositivos" detail="Nunca inició sesión en la app móvil." />
            ) : (
              <ul className="flex flex-col gap-3 p-5">
                {devices.map((device) => (
                  <li key={device.id} className="flex items-center gap-2.5">
                    <span className="flex size-8 flex-none items-center justify-center rounded-md bg-secondary text-muted-foreground">
                      <Smartphone className="size-4" />
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-medium text-foreground">{device.platform}</span>
                      <span className="block truncate text-xs text-faint">
                        {device.deviceId} · visto {device.seen ?? "nunca"}
                      </span>
                    </span>
                    <Badge dot variant={device.active ? "success" : "neutral"}>
                      {device.active ? "Activo" : "Inactivo"}
                    </Badge>
                  </li>
                ))}
              </ul>
            )}
          </Widget>
        </div>
      </div>
    </div>
  );
}

function EmptyCard({ icon, title, detail }: { icon: ReactNode; title: string; detail: string }) {
  return (
    <Empty>
      <EmptyHeader>
        <EmptyMedia variant="icon">{icon}</EmptyMedia>
        <EmptyTitle>{title}</EmptyTitle>
        <EmptyDescription>{detail}</EmptyDescription>
      </EmptyHeader>
    </Empty>
  );
}


/**
 * Activar un plan a quien pagó por fuera de la app.
 *
 * La fecha de vencimiento no se escribe: se calcula y se muestra antes de
 * confirmar. Escribirla a mano es lo que dejó 139 membresías con una duración
 * que no corresponde a su plan.
 */
function ActivarPlan({
  planes,
  csrfToken,
}: {
  planes: { value: string; label: string; days: number; sessions: number; price: string | null }[];
  csrfToken: string;
}) {
  const [planId, setPlanId] = useState(planes[0]?.value ?? "");
  const [desde, setDesde] = useState(() => new Date().toISOString().slice(0, 10));
  const plan = planes.find((p) => p.value === planId);

  const vence = (() => {
    if (!plan || !desde) return null;
    const d = new Date(`${desde}T00:00:00`);
    if (Number.isNaN(d.getTime())) return null;
    d.setDate(d.getDate() + plan.days);
    return d.toLocaleDateString("es-CO", { day: "numeric", month: "long", year: "numeric" });
  })();

  if (!planes.length) return null;

  return (
    <form method="post" className="flex flex-col gap-3 border-t border-border p-5">
      <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
      <input type="hidden" name="action" value="activate-plan" />

      <p className="text-sm font-medium text-foreground">Activar un plan</p>
      <p className="-mt-2 text-xs text-muted-foreground">
        Para quien pagó en recepción. La fecha de vencimiento la pone el sistema.
      </p>

      <SelectField
        name="plan"
        label="Plan"
        defaultValue={planId}
        onChange={setPlanId}
        options={planes.map((p) => ({
          value: p.value,
          label: p.sessions ? `${p.label} — ${p.sessions} sesiones` : p.label,
        }))}
      />

      <TextField
        name="init_date"
        label="Desde"
        type="date"
        defaultValue={desde}
        onChange={(event: React.ChangeEvent<HTMLInputElement>) => setDesde(event.target.value)}
      />

      {plan && vence && (
        <p className="rounded-md border border-border bg-secondary px-3 py-2 text-xs text-muted-foreground">
          Vence el <span className="font-medium text-foreground">{vence}</span>
          {" "}({plan.days} días)
          {plan.sessions > 0 && (
            <>
              {" · "}
              <span className="font-medium text-foreground">{plan.sessions} sesiones</span>
              {" para agendar"}
            </>
          )}
        </p>
      )}

      <Button type="submit" size="sm" className="self-end">
        Activar plan
      </Button>
    </form>
  );
}
