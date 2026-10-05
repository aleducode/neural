import { ArrowRight, Bell, Users } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Table, TableCell, TableHead, TableRow } from "@/components/ui/table";

type Stat = { label: string; value: number; description: string };
type RecentUser = { id: number; name: string; initials: string; email: string; joined: string };
type RecentNotification = {
  id: number;
  title: string;
  userName: string;
  status: string;
  statusLabel: string;
};

type Props = {
  stats: Stat[];
  users: RecentUser[];
  notifications: RecentNotification[];
  usersUrl: string;
  notificationsUrl: string;
  userDetailUrl: string;
};

function badgeFor(status: string) {
  if (status === "sent" || status === "delivered") return "success" as const;
  if (status === "failed") return "error" as const;
  if (status === "read") return "info" as const;
  return "neutral" as const;
}

function Empty({ icon, title, text }: { icon: JSX.Element; title: string; text: string }) {
  return (
    <div className="px-8 py-14 text-center">
      <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted text-muted-foreground">
        {icon}
      </div>
      <h5 className="mb-2 text-base font-semibold text-foreground">{title}</h5>
      <p className="text-sm text-muted-foreground">{text}</p>
    </div>
  );
}

export default function Dashboard({
  stats,
  users,
  notifications,
  usersUrl,
  notificationsUrl,
  userDetailUrl,
}: Props) {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label} className="p-5 transition-colors hover:border-slate-300">
            <div className="mb-1 text-xs font-medium uppercase tracking-wider text-muted-foreground">
              {stat.label}
            </div>
            <div className="text-3xl font-bold leading-none text-foreground">
              {stat.value.toLocaleString("es-CO")}
            </div>
            <div className="mt-2 text-xs text-muted-foreground">{stat.description}</div>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader className="flex items-start justify-between gap-4">
            <div>
              <CardTitle>Usuarios recientes</CardTitle>
              <CardDescription>Últimos usuarios registrados</CardDescription>
            </div>
            <Button variant="outline" size="sm" asChild>
              <a href={usersUrl}>
                Ver todos
                <ArrowRight className="h-4 w-4" />
              </a>
            </Button>
          </CardHeader>

          {users.length === 0 ? (
            <Empty
              icon={<Users className="h-6 w-6" />}
              title="Sin usuarios"
              text="No hay usuarios registrados aún."
            />
          ) : (
            <Table>
              <thead>
                <tr>
                  <TableHead>Usuario</TableHead>
                  <TableHead>Fecha</TableHead>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <a
                        href={userDetailUrl.replace("/0/", `/${user.id}/`)}
                        className="flex items-center gap-3 no-underline"
                      >
                        <span className="flex h-10 w-10 flex-none items-center justify-center rounded-full bg-emerald-500 text-sm font-semibold text-white">
                          {user.initials}
                        </span>
                        <span className="min-w-0">
                          <span className="block truncate text-sm font-medium text-foreground">
                            {user.name}
                          </span>
                          <span className="block truncate text-xs text-muted-foreground">
                            {user.email}
                          </span>
                        </span>
                      </a>
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-xs text-muted-foreground">
                      {user.joined}
                    </TableCell>
                  </TableRow>
                ))}
              </tbody>
            </Table>
          )}
        </Card>

        <Card>
          <CardHeader className="flex items-start justify-between gap-4">
            <div>
              <CardTitle>Notificaciones recientes</CardTitle>
              <CardDescription>Últimas notificaciones enviadas</CardDescription>
            </div>
            <Button variant="outline" size="sm" asChild>
              <a href={notificationsUrl}>
                Ver todas
                <ArrowRight className="h-4 w-4" />
              </a>
            </Button>
          </CardHeader>

          {notifications.length === 0 ? (
            <Empty
              icon={<Bell className="h-6 w-6" />}
              title="Sin notificaciones"
              text="No hay notificaciones enviadas aún."
            />
          ) : (
            <Table>
              <thead>
                <tr>
                  <TableHead>Notificación</TableHead>
                  <TableHead>Estado</TableHead>
                </tr>
              </thead>
              <tbody>
                {notifications.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      <div className="max-w-[250px]">
                        <div className="truncate text-sm font-medium text-foreground">
                          {item.title}
                        </div>
                        <div className="truncate text-xs text-muted-foreground">
                          {item.userName}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={badgeFor(item.status)}>{item.statusLabel}</Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </tbody>
            </Table>
          )}
        </Card>
      </div>
    </div>
  );
}
