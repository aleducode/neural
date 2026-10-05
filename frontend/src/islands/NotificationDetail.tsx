import { AlertTriangle, CheckCircle2, Smartphone } from "lucide-react";
import { useEffect, useState } from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { MemberAvatar } from "@/components/ui/member-avatar";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

/**
 * Modal de detalle de un envío.
 *
 * Los payloads de Expo son grandes, así que no viajan en el feed: el modal los
 * pide al abrirse. Es lo único que explica por qué falló un envío.
 */

export type Detail = {
  id: number;
  userName: string;
  userInitials: string;
  userPhoto: string | null;
  userEmail: string;
  userId: number;
  title: string;
  body: string;
  type: string;
  status: string;
  statusLabel: string;
  created: string | null;
  sentAt: string | null;
  readAt: string | null;
  scheduledFor: string | null;
  data: unknown;
  attempts: number;
  failures: number;
  summary: string | null;
  logs: {
    id: number;
    device: string;
    deviceId: string | null;
    deviceActive: boolean | null;
    token: string;
    ok: boolean;
    status: string;
    error: string | null;
    receipt: string | null;
    at: string | null;
    request: unknown;
    response: unknown;
  }[];
};

export const toneFor = (status: string) =>
  status === "delivered" || status === "sent"
    ? ("success" as const)
    : status === "failed"
      ? ("error" as const)
      : status === "read"
        ? ("info" as const)
        : ("neutral" as const);

export function NotificationDetailDialog({
  id,
  detailUrl,
  userDetailUrl,
  onClose,
}: {
  id: number | null;
  detailUrl: string;
  userDetailUrl: string;
  onClose: () => void;
}) {
  const [detail, setDetail] = useState<Detail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id === null) return;
    let vivo = true;
    setDetail(null);
    setError(null);
    fetch(detailUrl.replace("/0/", `/${id}/`), {
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then((response) => {
        if (!response.ok) throw new Error(`El servidor respondió ${response.status}`);
        return response.json();
      })
      .then((data) => vivo && setDetail(data))
      .catch((reason) => vivo && setError(String(reason.message ?? reason)));
    return () => {
      vivo = false;
    };
  }, [id, detailUrl]);

  return (
    <Dialog open={id !== null} onOpenChange={(abierto) => !abierto && onClose()}>
      <DialogContent className="max-h-[85vh] max-w-3xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Detalle del envío</DialogTitle>
          <DialogDescription>
            Qué se mandó, a qué dispositivos y qué respondió Expo.
          </DialogDescription>
        </DialogHeader>

        {error && (
          <Alert variant="destructive">
            <AlertTitle>No se pudo cargar el detalle</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {!detail && !error && (
          <div className="flex flex-col gap-3">
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-24 w-full" />
          </div>
        )}

        {detail && (
          <div className="flex flex-col gap-5">
            {detail.summary && (
              <Alert variant="destructive">
                <AlertTitle>
                  {detail.failures > 0
                    ? `Falló en ${detail.failures} de ${detail.attempts} dispositivos`
                    : "Sin envío registrado"}
                </AlertTitle>
                <AlertDescription>{detail.summary}</AlertDescription>
              </Alert>
            )}

            <section className="flex flex-col gap-3 rounded-lg border border-border bg-card p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <a
                  href={userDetailUrl.replace("/0/", `/${detail.userId}/`)}
                  className="flex items-center gap-2.5 no-underline"
                >
                  <MemberAvatar
                    name={detail.userName}
                    initials={detail.userInitials}
                    photo={detail.userPhoto}
                  />
                  <span className="min-w-0">
                    <span className="block truncate text-sm font-medium text-foreground">
                      {detail.userName}
                    </span>
                    <span className="block truncate text-xs text-muted-foreground">
                      {detail.userEmail}
                    </span>
                  </span>
                </a>
                <Badge dot variant={toneFor(detail.status)}>
                  {detail.statusLabel}
                </Badge>
              </div>

              <div>
                <p className="text-sm font-semibold text-foreground">{detail.title}</p>
                <p className="text-sm text-muted-foreground">{detail.body}</p>
              </div>

              <dl className="grid gap-x-6 gap-y-1.5 sm:grid-cols-2">
                {(
                  [
                    ["Tipo", detail.type],
                    ["Creada", detail.created],
                    ["Enviada", detail.sentAt],
                    ["Leída", detail.readAt],
                    ["Programada", detail.scheduledFor],
                  ] as [string, string | null][]
                )
                  .filter(([, value]) => value)
                  .map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between gap-3">
                      <dt className="text-xs text-muted-foreground">{key}</dt>
                      <dd className="text-xs font-medium text-foreground">{value}</dd>
                    </div>
                  ))}
              </dl>
            </section>

            <section className="flex flex-col gap-3">
              <h3 className="text-sm font-semibold text-foreground">
                Intentos de envío{" "}
                <span className="font-normal text-muted-foreground">
                  ({detail.attempts})
                </span>
              </h3>

              {detail.logs.length === 0 ? (
                <p className="rounded-lg border border-dashed border-border px-4 py-6 text-center text-sm text-muted-foreground">
                  No hay logs: la notificación se guardó pero nunca se intentó enviar.
                  Suele pasar cuando el usuario no tiene ningún dispositivo activo.
                </p>
              ) : (
                detail.logs.map((log) => (
                  <article
                    key={log.id}
                    className={cn(
                      "flex flex-col gap-3 rounded-lg border p-4",
                      log.ok ? "border-border bg-card" : "border-destructive/30 bg-negative-soft",
                    )}
                  >
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div className="flex min-w-0 items-center gap-2.5">
                        <span
                          className={cn(
                            "flex size-8 flex-none items-center justify-center rounded-md",
                            log.ok
                              ? "bg-positive-soft text-positive"
                              : "bg-background text-destructive",
                          )}
                        >
                          {log.ok ? (
                            <CheckCircle2 className="size-4" />
                          ) : (
                            <AlertTriangle className="size-4" />
                          )}
                        </span>
                        <span className="min-w-0">
                          <span className="flex items-center gap-2 text-sm font-medium text-foreground">
                            <Smartphone className="size-3.5 text-faint" aria-hidden="true" />
                            {log.device}
                            {log.deviceActive === false && (
                              <Badge variant="neutral">Dispositivo inactivo</Badge>
                            )}
                          </span>
                          <span className="block truncate font-mono text-xs text-muted-foreground">
                            {log.token}
                          </span>
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        {log.at && <span className="text-xs text-muted-foreground">{log.at}</span>}
                        <Badge dot variant={log.ok ? "success" : "error"}>
                          {log.status}
                        </Badge>
                      </div>
                    </div>

                    {log.error && (
                      <p className="rounded-md bg-background px-3 py-2 font-mono text-xs text-destructive">
                        {log.error}
                      </p>
                    )}

                    {log.receipt && (
                      <p className="text-xs text-muted-foreground">
                        Recibo de Expo: <span className="font-mono">{log.receipt}</span>
                      </p>
                    )}

                    <div className="grid gap-3 sm:grid-cols-2">
                      <Payload title="Enviado a Expo" value={log.request} />
                      <Payload title="Respuesta de Expo" value={log.response} />
                    </div>
                  </article>
                ))
              )}
            </section>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

/** El payload crudo, plegado: casi nunca se mira, pero cuando hace falta es esto. */
function Payload({ title, value }: { title: string; value: unknown }) {
  if (value === null || value === undefined) {
    return (
      <div className="min-w-0">
        <p className="mb-1 text-xs font-medium text-muted-foreground">{title}</p>
        <p className="text-xs text-faint">Sin respuesta (la petición nunca llegó).</p>
      </div>
    );
  }
  return (
    <details className="min-w-0">
      <summary className="cursor-pointer text-xs font-medium text-muted-foreground">
        {title}
      </summary>
      <pre className="mt-1.5 max-h-48 overflow-auto rounded-md bg-secondary p-3 font-mono text-[0.6875rem] leading-relaxed text-foreground">
        {JSON.stringify(value, null, 2)}
      </pre>
    </details>
  );
}
