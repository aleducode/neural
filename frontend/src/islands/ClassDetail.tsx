import {
  ArrowLeft,
  CalendarDays,
  ClipboardList,
  Clock3,
  Dumbbell,
  History,
  Trophy,
  Users,
} from "lucide-react";
import type { ReactNode } from "react";

import { MemberAvatar } from "@/components/ui/member-avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DetailHero,
  Field,
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
import { OccupancyBar } from "@/components/ui/occupancy-bar";
import { StatWidget, type Kpi } from "@/components/ui/stat-widget";
import { Table, TableCell, TableHead, TableRow } from "@/components/ui/table";
import { Widget, WidgetHeader } from "@/components/ui/widget";

type Errors = Record<string, { message: string }[]>;

type Props = {
  klass: {
    id: number;
    typeId: number;
    name: string;
    kind: string;
    day: string;
    time: string;
    duration: string;
    places: number | null;
    photo: string;
  };
  kpis: Kpi[];
  form: {
    name: string;
    is_group: boolean;
    day: string;
    hour_init: string;
    hour_end: string;
    photo: string;
    hasPhoto: boolean;
  };
  dayChoices: { value: string; label: string }[];
  sessions: { id: number; date: string | null; taken: number; places: number; occupancy: number; status: string; tone: Tone }[];
  nextDate: string | null;
  enrolled: { id: number; userId: number; name: string; initials: string; photo: string | null; email: string; plan: string; booked: string | null; status: string; tone: Tone }[];
  weekly: { label: string; value: number }[];
  weeklyAverage: number;
  frequent: { id: number; name: string; initials: string; photo: string | null; count: number }[];
  history: [string, string][];
  errors?: Errors;
  csrfToken: string;
  backUrl: string;
  calendarUrl: string;
  userDetailUrl: string;
};

const err = (errors: Errors | undefined, field: string) => errors?.[field]?.[0]?.message;

export default function ClassDetail({
  klass,
  kpis,
  form,
  dayChoices,
  sessions,
  nextDate,
  enrolled,
  weekly,
  weeklyAverage,
  frequent,
  history,
  errors,
  csrfToken,
  backUrl,
  calendarUrl,
  userDetailUrl,
}: Props) {
  return (
    <div className="flex flex-col gap-6">
      <Button variant="ghost" size="sm" className="-ml-2 self-start" asChild>
        <a href={backUrl}>
          <ArrowLeft />
          Volver a clases
        </a>
      </Button>

      <DetailHero
        portrait={
          <img
            src={klass.photo}
            alt=""
            width={96}
            height={96}
            className="size-24 flex-none rounded-xl bg-secondary object-cover"
          />
        }
        title={klass.name}
        badges={[{ label: klass.kind, tone: "success" }]}
        meta={[
          { icon: CalendarDays, value: `Todos los ${klass.day.toLowerCase()}` },
          { icon: Clock3, value: `${klass.time} · ${klass.duration}` },
          ...(klass.places ? [{ icon: Users, value: `${klass.places} cupos por sesión` }] : []),
        ]}
        actions={
          <Button variant="outline" size="sm" asChild>
            <a href={calendarUrl}>
              <CalendarDays />
              Ver en calendario
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
            <WidgetHeader icon={<ClipboardList className="size-5" />} title="Ficha de la clase">
              <span className="text-xs text-muted-foreground">Editable por el equipo</span>
            </WidgetHeader>

            <form method="post" encType="multipart/form-data" className="flex flex-col">
              <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />

              <div className="flex flex-col gap-4 p-5">
                {err(errors, "__all__") && (
                  <p role="alert" className="text-sm text-destructive">
                    {err(errors, "__all__")}
                  </p>
                )}
                <div className="flex flex-wrap gap-4">
                  <TextField name="name" label="Tipo de entrenamiento" defaultValue={form.name} error={err(errors, "name")} />
                  <SelectField name="day" label="Día de la semana" defaultValue={form.day} options={dayChoices} error={err(errors, "day")} />
                </div>
                <div className="flex flex-wrap gap-4">
                  <TextField name="hour_init" label="Hora de inicio" type="time" defaultValue={form.hour_init} error={err(errors, "hour_init")} />
                  <TextField name="hour_end" label="Hora de fin" type="time" defaultValue={form.hour_end} error={err(errors, "hour_end")} />
                </div>

                <Field name="photo" label="Foto de la clase" error={err(errors, "photo")}>
                  <div className="flex flex-wrap items-center gap-3">
                    <img src={form.photo} alt="" className="size-[72px] flex-none rounded-xl bg-secondary object-cover" />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-foreground">
                        {form.hasPhoto ? "Foto propia" : "Foto de respaldo"}
                      </p>
                      <p className="text-xs text-faint">
                        Se ve en el dashboard, en «Clases más pedidas». 320×352 o mayor.
                      </p>
                    </div>
                    <input
                      id="photo"
                      type="file"
                      name="photo"
                      accept="image/*"
                      className="max-w-56 text-xs text-muted-foreground file:mr-2 file:rounded-md file:border file:border-border file:bg-background file:px-3 file:py-1.5 file:text-xs file:font-medium file:text-foreground"
                    />
                  </div>
                </Field>

                <label className="flex items-center gap-2 text-sm text-muted-foreground">
                  <input
                    type="checkbox"
                    name="is_group"
                    defaultChecked={form.is_group}
                    className="size-4 rounded-sm border-border accent-[hsl(var(--primary))]"
                  />
                  Es una clase grupal
                </label>
              </div>

              <FormFooter hint="El cupo vive en cada sesión, no en el horario: cambiarlo acá no mueve las sesiones ya creadas.">
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
            <WidgetHeader icon={<CalendarDays className="size-5" />} title="Próximas sesiones">
              <span className="text-xs text-muted-foreground">Siguientes 5</span>
            </WidgetHeader>
            {sessions.length === 0 ? (
              <EmptyCard icon={<CalendarDays />} title="Sin sesiones programadas" detail="No hay ningún slot futuro creado para este horario." />
            ) : (
              <Table>
                <thead>
                  <tr>
                    <TableHead>Fecha</TableHead>
                    <TableHead>Reservas</TableHead>
                    <TableHead>Ocupación</TableHead>
                    <TableHead>Estado</TableHead>
                  </tr>
                </thead>
                <tbody>
                  {sessions.map((row) => (
                    <TableRow key={row.id}>
                      <TableCell className="whitespace-nowrap text-sm font-medium text-foreground">{row.date ?? "—"}</TableCell>
                      <TableCell className="whitespace-nowrap text-sm tabular-nums text-muted-foreground">
                        {row.taken} / {row.places}
                      </TableCell>
                      <TableCell>
                        <OccupancyBar value={row.occupancy} />
                      </TableCell>
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
            <WidgetHeader
              icon={<Users className="size-5" />}
              title={nextDate ? `Inscritos · ${nextDate}` : "Inscritos"}
            >
              <span className="text-xs text-muted-foreground">
                {enrolled.filter((e) => e.tone !== "error").length} confirmados
              </span>
            </WidgetHeader>
            {enrolled.length === 0 ? (
              <EmptyCard icon={<Users />} title="Nadie inscrito todavía" detail="La próxima sesión aún no tiene reservas." />
            ) : (
              <Table>
                <thead>
                  <tr>
                    <TableHead>Usuario</TableHead>
                    <TableHead>Membresía</TableHead>
                    <TableHead>Reservó</TableHead>
                    <TableHead>Estado</TableHead>
                  </tr>
                </thead>
                <tbody>
                  {enrolled.map((row) => (
                    <TableRow key={row.id}>
                      <TableCell>
                        <a href={userDetailUrl.replace("/0/", `/${row.userId}/`)} className="flex items-center gap-2.5 no-underline">
                          <MemberAvatar name={row.name} initials={row.initials} photo={row.photo} />
                          <span className="min-w-0">
                            <span className="block truncate text-sm font-medium text-foreground">{row.name}</span>
                            <span className="block truncate text-xs text-muted-foreground">{row.email}</span>
                          </span>
                        </a>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">{row.plan}</TableCell>
                      <TableCell className="whitespace-nowrap text-sm text-muted-foreground">{row.booked ?? "—"}</TableCell>
                      <TableCell>
                        <Badge dot variant={row.tone}>{row.status}</Badge>
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
            <WidgetHeader icon={<Dumbbell className="size-5" />} title="Ocupación">
              <span className="text-xs text-muted-foreground">12 semanas</span>
            </WidgetHeader>
            <div className="flex flex-col gap-3 p-5">
              <p className="flex items-center gap-2">
                <span className="text-2xl font-semibold tabular-nums text-foreground">{weeklyAverage}%</span>
                <span className="text-sm text-muted-foreground">promedio de ocupación</span>
              </p>
              <WeekBars points={weekly} suffix="%" />
            </div>
          </Widget>

          <Widget>
            <WidgetHeader icon={<Trophy className="size-5" />} title="Más frecuentes">
              <span className="text-xs text-muted-foreground">Histórico</span>
            </WidgetHeader>
            {frequent.length === 0 ? (
              <EmptyCard icon={<Trophy />} title="Sin asistencias" detail="Nadie ha entrenado en este horario todavía." />
            ) : (
              <ul className="flex flex-col gap-3 p-5">
                {frequent.map((row) => (
                  <li key={row.id}>
                    <a href={userDetailUrl.replace("/0/", `/${row.id}/`)} className="flex items-center gap-2.5 no-underline">
                      <MemberAvatar name={row.name} initials={row.initials} photo={row.photo} />
                      <span className="min-w-0 flex-1 truncate text-sm font-medium text-foreground">{row.name}</span>
                      <span className="text-xs tabular-nums text-faint">{row.count} asistencias</span>
                    </a>
                  </li>
                ))}
              </ul>
            )}
          </Widget>

          <Widget>
            <WidgetHeader icon={<History className="size-5" />} title="Histórico">
              <span className="text-xs text-muted-foreground">Desde el inicio</span>
            </WidgetHeader>
            <dl className="flex flex-col gap-2.5 p-5">
              {history.map(([key, value]) => (
                <KeyValue key={key} term={key}>
                  {value}
                </KeyValue>
              ))}
            </dl>
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
