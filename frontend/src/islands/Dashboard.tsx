import {
  ArrowRight,
  BellPlus,
  CalendarClock,
  CreditCard,
  Flame,
  LineChart,
  Wallet,
} from "lucide-react";

import GrowthChart, { type GrowthPoint, type GrowthSeries } from "@/components/charts/GrowthChart";
import RevenueDonut, { type Segment } from "@/components/charts/RevenueDonut";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { MemberAvatar } from "@/components/ui/member-avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty";
import { StatWidget, type Kpi } from "@/components/ui/stat-widget";
import { Table, TableCell, TableHead, TableRow } from "@/components/ui/table";
import { DeltaPill, Widget, WidgetHeader } from "@/components/ui/widget";

type PopularClass = {
  id: number;
  name: string;
  kind: string;
  duration: string | null;
  bookings: number;
  image: string;
};

type Payment = {
  id: number;
  userId: number;
  reference: string;
  name: string;
  initials: string;
  photo: string | null;
  plan: string;
  amount: string;
  date: string;
  paid: boolean;
  status: string;
};

type Props = {
  today: string;
  kpis: Kpi[];
  growth: {
    points: GrowthPoint[];
    total: number;
    delta: number | null;
    range: string;
    series: GrowthSeries[];
  };
  classes: PopularClass[];
  revenue: { segments: Segment[]; total: string; period: string };
  payments: Payment[];
  gaps: string[];
  usersUrl: string;
  userDetailUrl: string;
  sendUrl: string;
};

export default function Dashboard({
  today,
  kpis,
  growth,
  classes,
  revenue,
  payments,
  gaps,
  usersUrl,
  userDetailUrl,
  sendUrl,
}: Props) {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Dashboard</h1>
          <p className="text-base text-muted-foreground">
            Usuarios, ingresos y ocupación · {today}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button variant="outline" size="sm" asChild>
            <a href={sendUrl}>
              <BellPlus />
              Enviar notificación
            </a>
          </Button>
          <Button size="sm" asChild>
            <a href={usersUrl}>
              Ver usuarios
              <ArrowRight />
            </a>
          </Button>
        </div>
      </header>

      {gaps.length > 0 && (
        <Alert>
          <AlertTitle>Faltan datos para algunos widgets</AlertTitle>
          <AlertDescription>
            Hay widgets vacíos porque {gaps.join(" y ")}. Lo que ves abajo es lo que el sistema
            tiene, no un ejemplo.
          </AlertDescription>
        </Alert>
      )}

      <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.map((kpi) => (
          <StatWidget {...kpi} key={kpi.key} />
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_372px]">
        <Widget className="min-h-[400px]">
          <WidgetHeader icon={<LineChart className="size-5" />} title="Crecimiento de usuarios" />

          {/* Cabecera de datos: el numero heroe, su variacion y la leyenda.
              Con dos series la leyenda no es opcional. */}
          <div className="flex flex-wrap items-center justify-between gap-4 p-5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-2xl font-semibold tabular-nums text-foreground">
                {growth.total}
              </span>
              <DeltaPill delta={growth.delta} basis="entre el primer y el último mes" />
              <span className="text-sm text-muted-foreground">usuarios nuevos {growth.range}</span>
            </div>
            <ul className="flex items-center gap-3">
              {growth.series.map((serie) => (
                <li key={serie.key} className="flex items-center gap-1.5">
                  <span
                    className="size-2 flex-none rounded-sm"
                    style={{
                      background: serie.key === "newUsers" ? "var(--series-1)" : "var(--series-2)",
                    }}
                    aria-hidden="true"
                  />
                  <span className="text-sm text-muted-foreground">{serie.label}</span>
                </li>
              ))}
            </ul>
          </div>

          <GrowthChart points={growth.points} series={growth.series} />
        </Widget>

        <Widget className="min-h-[400px]">
          <WidgetHeader icon={<Flame className="size-5" />} title="Clases más pedidas">
            <span className="text-xs text-muted-foreground">Últimos 30 días</span>
          </WidgetHeader>

          {classes.length === 0 ? (
            <Empty>
              <EmptyHeader>
                <EmptyMedia variant="icon">
                  <Flame />
                </EmptyMedia>
                <EmptyTitle>Sin reservas este mes</EmptyTitle>
                <EmptyDescription>
                  Ningún tipo de entrenamiento tuvo reservas en los últimos 30 días.
                </EmptyDescription>
              </EmptyHeader>
            </Empty>
          ) : (
            <ul className="flex flex-col gap-4 p-5">
              {classes.map((item) => (
                <li
                  key={item.id}
                  className="flex items-center gap-3 rounded-xl border border-border p-3"
                >
                  {/* Foto del tipo de entrenamiento (TrainingType.photo), con
                      una de respaldo mientras el gimnasio no suba la suya. */}
                  <img
                    src={item.image}
                    alt=""
                    width={80}
                    height={88}
                    loading="lazy"
                    className="h-[88px] w-20 flex-none rounded-xl bg-secondary object-cover"
                  />
                  <div className="flex min-w-0 flex-1 flex-col gap-2">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-foreground">{item.name}</p>
                      <p className="text-xs text-faint">{item.kind}</p>
                    </div>
                    <div className="flex items-center justify-between gap-3 text-xs text-faint">
                      <span className="flex items-center gap-1">
                        <CalendarClock className="size-4" aria-hidden="true" />
                        {item.duration ?? "Sin horario fijo"}
                      </span>
                      <span className="tabular-nums">{item.bookings} reservas</span>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Widget>
      </div>

      <div className="grid gap-6 xl:grid-cols-[372px_minmax(0,1fr)]">
        <Widget className="min-h-[400px]">
          <WidgetHeader icon={<Wallet className="size-5" />} title="Ingresos por plan">
            <span className="text-xs text-muted-foreground">{revenue.period}</span>
          </WidgetHeader>
          <RevenueDonut {...revenue} />
        </Widget>

        <Widget>
          <WidgetHeader icon={<CreditCard className="size-5" />} title="Últimos pagos" />

          {payments.length === 0 ? (
            <Empty>
              <EmptyHeader>
                <EmptyMedia variant="icon">
                  <CreditCard />
                </EmptyMedia>
                <EmptyTitle>Sin pagos registrados</EmptyTitle>
                <EmptyDescription>
                  Todavía no hay ninguna referencia de pago en el sistema.
                </EmptyDescription>
              </EmptyHeader>
            </Empty>
          ) : (
            <Table className="min-w-[640px]">
              <thead>
                <tr>
                  <TableHead>Referencia</TableHead>
                  <TableHead>Usuario</TableHead>
                  <TableHead>Monto</TableHead>
                  <TableHead>Fecha</TableHead>
                  <TableHead>Estado</TableHead>
                </tr>
              </thead>
              <tbody>
                {payments.map((payment) => (
                  <TableRow key={payment.id}>
                    <TableCell className="text-sm font-medium tabular-nums text-foreground">
                      {payment.reference}
                    </TableCell>
                    <TableCell>
                      <a
                        href={userDetailUrl.replace("/0/", `/${payment.userId}/`)}
                        className="flex items-center gap-2.5 no-underline"
                      >
                        <MemberAvatar
                          name={payment.name}
                          initials={payment.initials}
                          photo={payment.photo}
                        />
                        <span className="min-w-0">
                          <span className="block truncate text-sm font-medium text-foreground">
                            {payment.name}
                          </span>
                          <span className="block truncate text-xs text-muted-foreground">
                            {payment.plan}
                          </span>
                        </span>
                      </a>
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-sm font-medium tabular-nums text-foreground">
                      {payment.amount}
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-sm text-foreground">
                      {payment.date}
                    </TableCell>
                    <TableCell>
                      <Badge dot variant={payment.paid ? "success" : "neutral"}>
                        {payment.status}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </tbody>
            </Table>
          )}
        </Widget>
      </div>
    </div>
  );
}
