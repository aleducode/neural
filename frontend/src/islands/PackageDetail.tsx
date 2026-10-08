import {
  ArrowLeft,
  ChevronDown,
  ChevronUp,
  Clock3,
  Library,
  Plus,
  Trash2,
  TrendingUp,
  Users,
  Video as VideoIcon,
} from "lucide-react";
import { useState, type ReactNode } from "react";

import { Button } from "@/components/ui/button";
import {
  DetailHero,
  Field,
  FormFooter,
  SelectField,
  TextField,
  type Tone,
} from "@/components/ui/detail";
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty";
import { MemberAvatar } from "@/components/ui/member-avatar";
import { ProgressBar } from "@/components/ui/progress-bar";
import { StatWidget, type Kpi } from "@/components/ui/stat-widget";
import { UserPicker, type PickerUser } from "@/components/ui/user-picker";
import { VideoThumb } from "@/components/ui/video-thumb";
import { Widget, WidgetHeader } from "@/components/ui/widget";

type Errors = Record<string, { message: string }[]>;
type Choice = { value: string; label: string };

type Item = {
  id: number;
  videoId: number;
  order: number;
  notes: string;
  name: string;
  poster: string | null;
  playback: string | null;
  duration: string;
  sourceLabel: string;
  level: string;
  published: boolean;
};

type Props = {
  package: {
    id: number;
    name: string;
    description: string;
    cover: string | null;
    kind: string;
    kindLabel: string;
    published: boolean;
  };
  kpis: Kpi[];
  items: Item[];
  assignments: {
    id: number;
    label: string;
    sub: string;
    kind: string;
    userId: number | null;
    initials: string | null;
  }[];
  available: { id: number; name: string; duration: string; source: string; poster: string | null }[];
  drafts: number;
  progress: {
    videos: { id: number; name: string; poster: string | null; duration: string; viewers: number; completed: number; average: number }[];
    members: { id: number; name: string; initials: string; photo: string | null; done: number; videos: number; percent: number; lastSeen: string | null }[];
    started: number;
    finished: number;
  };
  kindChoices: Choice[];
  plans: Choice[];
  users: PickerUser[];
  errors?: Errors;
  csrfToken: string;
  backUrl: string;
  userDetailUrl: string;
  videoListUrl: string;
};

const err = (errors: Errors | undefined, field: string) => errors?.[field]?.[0]?.message;

export default function PackageDetail({
  package: paquete,
  kpis,
  items,
  assignments,
  available,
  drafts,
  progress,
  kindChoices,
  plans,
  users,
  errors,
  csrfToken,
  backUrl,
  userDetailUrl,
  videoListUrl,
}: Props) {
  const [destino, setDestino] = useState("user");

  return (
    <div className="flex flex-col gap-6">
      <Button variant="ghost" size="sm" className="-ml-2 self-start" asChild>
        <a href={backUrl}>
          <ArrowLeft />
          Volver a paquetes
        </a>
      </Button>

      <DetailHero
        portrait={<VideoThumb poster={paquete.cover} name={paquete.name} className="h-24 w-40" />}
        title={paquete.name}
        badges={[
          { label: paquete.kindLabel, tone: paquete.kind === "individual" ? "warning" : "success" },
          { label: paquete.published ? "Publicado" : "Borrador", tone: paquete.published ? "success" : "neutral" as Tone },
        ]}
        meta={[
          { icon: VideoIcon, value: `${items.length} videos` },
          { icon: Users, value: `${assignments.length} asignaciones` },
        ]}
      />

      <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.map((kpi) => (
          <StatWidget {...kpi} key={kpi.key} />
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_364px] xl:items-start">
        <div className="flex flex-col gap-6">
          <Widget>
            <WidgetHeader icon={<VideoIcon className="size-5" />} title="Videos del paquete">
              <span className="text-xs text-muted-foreground">
                El orden es el que ve el usuario
              </span>
            </WidgetHeader>

            {items.length === 0 ? (
              <EmptyCard
                icon={<VideoIcon />}
                title="Paquete vacío"
                detail="Agregá videos desde el panel de la derecha."
              />
            ) : (
              <ol className="flex flex-col divide-y divide-border">
                {items.map((item, index) => (
                  <li key={item.id} className="flex flex-wrap items-center gap-3 px-5 py-3">
                    <span className="w-6 flex-none text-sm font-medium tabular-nums text-muted-foreground">
                      {index + 1}
                    </span>
                    <VideoThumb poster={item.poster} name={item.name} />
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-medium text-foreground">
                        {item.name}
                      </span>
                      <span className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Clock3 className="size-3.5" aria-hidden="true" />
                        {item.duration} · {item.sourceLabel}
                        {!item.published && (
                          <span className="text-destructive">· sin publicar</span>
                        )}
                      </span>
                    </span>

                    {/* Mover y quitar son formularios: sin JavaScript también
                        funcionan, que es lo que el panel promete. */}
                    <span className="flex items-center gap-1">
                      <Accion
                        csrfToken={csrfToken}
                        action="move-video"
                        extra={{ item: item.id, dir: "up" }}
                        label="Subir"
                        disabled={index === 0}
                      >
                        <ChevronUp />
                      </Accion>
                      <Accion
                        csrfToken={csrfToken}
                        action="move-video"
                        extra={{ item: item.id, dir: "down" }}
                        label="Bajar"
                        disabled={index === items.length - 1}
                      >
                        <ChevronDown />
                      </Accion>
                      <Accion
                        csrfToken={csrfToken}
                        action="remove-video"
                        extra={{ item: item.id }}
                        label="Quitar del paquete"
                        destructive
                      >
                        <Trash2 />
                      </Accion>
                    </span>

                    {/* La indicacion del entrenador para este video en este
                        modulo. Es lo que el socio lee arriba del reproductor. */}
                    <form method="post" className="flex w-full items-center gap-2 pl-9">
                      <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
                      <input type="hidden" name="action" value="note" />
                      <input type="hidden" name="item" value={item.id} />
                      <input
                        name="notes"
                        defaultValue={item.notes}
                        maxLength={500}
                        placeholder="Nota para el socio: «3 series de 12»"
                        className="h-8 min-w-0 flex-1 rounded-md border border-input bg-background px-3 text-xs text-foreground outline-none placeholder:text-faint focus-visible:ring-2 focus-visible:ring-ring"
                      />
                      <button
                        type="submit"
                        className="h-8 flex-none rounded-md border border-border px-3 text-xs font-medium text-foreground hover:bg-secondary"
                      >
                        Guardar nota
                      </button>
                    </form>
                  </li>
                ))}
              </ol>
            )}
          </Widget>

          <Widget>
            <WidgetHeader icon={<TrendingUp className="size-5" />} title="Consumo por video">
              <span className="text-xs text-muted-foreground">
                {progress.started} empezaron · {progress.finished} lo terminaron
              </span>
            </WidgetHeader>
            {progress.videos.length === 0 ? (
              <EmptyCard
                icon={<TrendingUp />}
                title="Sin datos de consumo"
                detail="Nadie ha abierto todavía los videos de este paquete."
              />
            ) : (
              <ul className="flex flex-col divide-y divide-border">
                {progress.videos.map((v) => (
                  <li key={v.id} className="flex items-center gap-3 px-5 py-3">
                    <VideoThumb poster={v.poster} name={v.name} className="h-9 w-14" />
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-medium text-foreground">
                        {v.name}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {v.viewers === 0
                          ? "Nadie lo abrió"
                          : `${v.viewers} lo abrieron · ${v.completed} lo terminaron`}
                      </span>
                    </span>
                    {/* El promedio de avance es lo que delata un video que la
                        gente abandona a la mitad. */}
                    <ProgressBar percent={v.average} done={v.average >= 100} />
                  </li>
                ))}
              </ul>
            )}
          </Widget>

          <Widget>
            <WidgetHeader icon={<Library className="size-5" />} title="Ficha del paquete">
              <span className="text-xs text-muted-foreground">Editable por el equipo</span>
            </WidgetHeader>
            <form method="post" encType="multipart/form-data" className="flex flex-col">
              <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
              <input type="hidden" name="action" value="save" />
              <div className="flex flex-col gap-4 p-5">
                <div className="flex flex-wrap gap-4">
                  <TextField name="name" label="Nombre" defaultValue={paquete.name} error={err(errors, "name")} />
                  <SelectField name="kind" label="Modalidad" defaultValue={paquete.kind} options={kindChoices} error={err(errors, "kind")} />
                </div>
                <Field name="description" label="Descripción" error={err(errors, "description")}>
                  <textarea
                    id="description"
                    name="description"
                    rows={3}
                    defaultValue={paquete.description}
                    className="rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  />
                </Field>
                <Field name="cover" label="Portada" error={err(errors, "cover")}>
                  <input
                    id="cover"
                    type="file"
                    name="cover"
                    accept="image/*"
                    className="max-w-sm text-xs text-muted-foreground file:mr-2 file:rounded-md file:border file:border-border file:bg-background file:px-3 file:py-1.5 file:text-xs file:font-medium file:text-foreground"
                  />
                </Field>
                <label className="flex items-center gap-2 text-sm text-muted-foreground">
                  <input
                    type="checkbox"
                    name="is_published"
                    defaultChecked={paquete.published}
                    className="size-4 rounded-sm border-border accent-[hsl(var(--primary))]"
                  />
                  Publicado (visible en la app)
                </label>
              </div>
              <FormFooter hint="Un paquete sin publicar no le llega a nadie, aunque esté asignado.">
                <Button type="submit" size="sm">
                  Guardar cambios
                </Button>
              </FormFooter>
            </form>
          </Widget>
        </div>

        <div className="flex flex-col gap-6">
          <Widget>
            <WidgetHeader icon={<Plus className="size-5" />} title="Agregar videos">
              <span className="text-xs text-muted-foreground">{available.length} disponibles</span>
            </WidgetHeader>
            {available.length === 0 ? (
              <div className="p-5 text-center">
                <p className="text-sm text-muted-foreground">
                  {drafts > 0
                    ? `Hay ${drafts} video${drafts === 1 ? "" : "s"} en borrador. Publicalos en la biblioteca para poder agregarlos.`
                    : "No queda ningún video publicado fuera de este paquete."}
                </p>
                <Button variant="outline" size="sm" className="mt-3" asChild>
                  <a href={videoListUrl}>Ir a la biblioteca</a>
                </Button>
              </div>
            ) : (
              <ul className="flex max-h-96 flex-col divide-y divide-border overflow-y-auto">
                {available.map((video) => (
                  <li key={video.id} className="flex items-center gap-2.5 px-5 py-2.5">
                    <VideoThumb poster={video.poster} name={video.name} className="h-9 w-14" />
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm text-foreground">{video.name}</span>
                      <span className="block text-xs text-faint">
                        {video.duration} · {video.source}
                      </span>
                    </span>
                    <Accion
                      csrfToken={csrfToken}
                      action="add-video"
                      extra={{ video: video.id }}
                      label={`Agregar ${video.name}`}
                    >
                      <Plus />
                    </Accion>
                  </li>
                ))}
              </ul>
            )}
          </Widget>

          <Widget>
            <WidgetHeader icon={<TrendingUp className="size-5" />} title="Quién va adelante">
              <span className="text-xs text-muted-foreground">Top 20</span>
            </WidgetHeader>
            {progress.members.length === 0 ? (
              <p className="p-5 text-sm text-muted-foreground">
                Todavía nadie abrió un video de este paquete.
              </p>
            ) : (
              <ul className="flex flex-col gap-3 p-5">
                {progress.members.map((m) => (
                  <li key={m.id}>
                    <a
                      href={userDetailUrl.replace("/0/", `/${m.id}/`)}
                      className="flex items-center gap-2.5 no-underline"
                    >
                      <MemberAvatar name={m.name} initials={m.initials} photo={m.photo} />
                      <span className="min-w-0 flex-1">
                        <span className="block truncate text-sm font-medium text-foreground">
                          {m.name}
                        </span>
                        <span className="flex items-center gap-2">
                          <ProgressBar
                            percent={m.percent}
                            done={m.done === m.videos}
                            width="w-16"
                          />
                          <span className="text-[0.625rem] text-faint">
                            {m.done}/{m.videos} · {m.lastSeen}
                          </span>
                        </span>
                      </span>
                    </a>
                  </li>
                ))}
              </ul>
            )}
          </Widget>

          <Widget>
            <WidgetHeader icon={<Users className="size-5" />} title="Asignado a" />
            <div className="flex flex-col gap-3 p-5">
              {assignments.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  Nadie todavía. Mientras no se asigne, no le llega a ningún usuario.
                </p>
              ) : (
                <ul className="flex flex-col gap-2">
                  {assignments.map((a) => (
                    <li key={a.id} className="flex items-center gap-2.5 rounded-md bg-secondary px-3 py-2">
                      {a.kind === "user" ? (
                        <MemberAvatar name={a.label} initials={a.initials ?? "?"} />
                      ) : (
                        <span className="flex size-8 flex-none items-center justify-center rounded-full bg-background text-muted-foreground">
                          <Users className="size-4" />
                        </span>
                      )}
                      <span className="min-w-0 flex-1">
                        <span className="block truncate text-sm font-medium text-foreground">
                          {a.kind === "user" && a.userId ? (
                            <a
                              href={userDetailUrl.replace("/0/", `/${a.userId}/`)}
                              className="no-underline hover:underline"
                            >
                              {a.label}
                            </a>
                          ) : (
                            a.label
                          )}
                        </span>
                        <span className="block truncate text-xs text-muted-foreground">{a.sub}</span>
                      </span>
                      <Accion
                        csrfToken={csrfToken}
                        action="unassign"
                        extra={{ assignment: a.id }}
                        label={`Quitar ${a.label}`}
                        destructive
                      >
                        <Trash2 />
                      </Accion>
                    </li>
                  ))}
                </ul>
              )}

              <form method="post" className="flex flex-col gap-3 border-t border-border pt-4">
                <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
                <input type="hidden" name="action" value="assign" />
                <SelectField
                  name="target"
                  label="Nuevo destino"
                  defaultValue={destino}
                  options={[
                    { value: "user", label: "Un usuario" },
                    { value: "plan", label: "Un plan" },
                    { value: "everyone", label: "Todos los usuarios" },
                  ]}
                  onChange={setDestino}
                  error={err(errors, "target")}
                />
                {destino === "user" && (
                  <UserPicker
                    name="users"
                    label="Usuarios"
                    users={users}
                    error={err(errors, "users")}
                  />
                )}
                {destino === "plan" && (
                  <SelectField name="plan" label="Plan" options={plans} error={err(errors, "plan")} />
                )}
                <Button type="submit" size="sm" variant="outline">
                  Asignar
                </Button>
              </form>
            </div>
          </Widget>
        </div>
      </div>
    </div>
  );
}

/** Un botón que es un formulario: una acción del constructor, sin JavaScript. */
function Accion({
  csrfToken,
  action,
  extra,
  label,
  children,
  disabled,
  destructive,
}: {
  csrfToken: string;
  action: string;
  extra: Record<string, string | number>;
  label: string;
  children: ReactNode;
  disabled?: boolean;
  destructive?: boolean;
}) {
  return (
    <form method="post" className="contents">
      <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
      <input type="hidden" name="action" value={action} />
      {Object.entries(extra).map(([key, value]) => (
        <input key={key} type="hidden" name={key} value={value} />
      ))}
      <Button
        type="submit"
        variant="ghost"
        size="icon"
        className={destructive ? "size-8 text-destructive" : "size-8"}
        disabled={disabled}
        aria-label={label}
        title={label}
      >
        {children}
      </Button>
    </form>
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
