import { CheckCircle2, CloudUpload, RotateCw, X } from "lucide-react";
import { useCallback, useRef, useState } from "react";
import * as tus from "tus-js-client";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

/**
 * Sube un video, por partes, pensado para internet malo.
 *
 * Dos caminos, y lo decide el servidor, no el navegador:
 *  - `stream`: Cloudflare da una URL de un solo uso y el archivo va **directo**
 *    allá por tus. Nunca pasa por Django: sin peticiones de diez minutos ni
 *    límite de body. Reanudable por el propio protocolo.
 *  - `fallback`: no hay token de Cloudflare, así que los trozos van a nuestro
 *    almacenamiento. También reanudable, preguntando qué partes ya llegaron.
 *
 * El componente es el mismo en los dos casos; lo que cambia es a dónde manda.
 */

const CHUNK = 5 * 1024 * 1024; // 5 MB: el mínimo que Cloudflare acepta por parte
const REINTENTOS = 3;

type Estado = "idle" | "subiendo" | "pausada" | "listo" | "error";
type Modo = "stream" | "fallback" | null;

const espera = (ms: number) => new Promise((r) => setTimeout(r, ms));
const mb = (bytes: number) => `${(bytes / (1024 * 1024)).toFixed(1)} MB`;

export function ChunkedUpload({
  uploadUrl,
  csrfToken,
  onDone,
}: {
  uploadUrl: string;
  csrfToken: string;
  onDone?: (video: { videoId: number; name: string }) => void;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [estado, setEstado] = useState<Estado>("idle");
  const [modo, setModo] = useState<Modo>(null);
  const [pct, setPct] = useState(0);
  const [detalle, setDetalle] = useState("");
  const [error, setError] = useState<string | null>(null);
  const cancelado = useRef(false);
  const subidaTus = useRef<tus.Upload | null>(null);

  const pedir = useCallback(
    async (campos: Record<string, string | Blob>) => {
      const body = new FormData();
      body.append("csrfmiddlewaretoken", csrfToken);
      for (const [k, v] of Object.entries(campos)) body.append(k, v);
      const response = await fetch(uploadUrl, { method: "POST", body });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error ?? `Error ${response.status}`);
      return data;
    },
    [uploadUrl, csrfToken],
  );

  /** Directo a Cloudflare con tus: él solo reanuda y reintenta. */
  const aStream = useCallback(
    (elegido: File, destino: string, uid: string) =>
      new Promise<void>((resolve, reject) => {
        const upload = new tus.Upload(elegido, {
          uploadUrl: destino,
          chunkSize: CHUNK,
          retryDelays: [0, 3000, 6000, 12000],
          metadata: { name: elegido.name, filetype: elegido.type },
          onProgress: (subido, total) => {
            setPct(Math.round((subido / total) * 100));
            setDetalle(`${mb(subido)} de ${mb(total)}`);
          },
          onError: reject,
          onSuccess: async () => {
            // Los bytes ya llegaron, pero Cloudflare sigue codificando: la
            // duración y el "listo" todavía no existen. Se vuelve a preguntar
            // unas cuantas veces; si igual no alcanza, `sync_stream_videos` lo
            // levanta después.
            for (let intento = 0; intento < 6; intento++) {
              setDetalle(`Procesando en Cloudflare… (${intento * 5}s)`);
              const estado = await pedir({ action: "confirm", uid });
              if (estado.ready) {
                setDetalle(`Listo · ${Math.round(estado.duration)}s`);
                break;
              }
              await espera(5000);
            }
            resolve();
          },
        });
        subidaTus.current = upload;
        upload.start();
      }),
    [pedir],
  );

  /** A nuestro almacenamiento, preguntando qué partes ya llegaron. */
  const aNuestro = useCallback(
    async (elegido: File) => {
      const sesion = await pedir({
        action: "init",
        filename: elegido.name,
        size: String(elegido.size),
        chunkSize: String(CHUNK),
      });
      const tam: number = sesion.chunkSize;
      const cuantos: number = sesion.totalChunks;
      const yaEstan = new Set<number>(sesion.received ?? []);
      let hechos = yaEstan.size;
      setPct(Math.round((hechos / cuantos) * 100));

      for (let i = 0; i < cuantos; i++) {
        if (cancelado.current) {
          setEstado("pausada");
          return null;
        }
        if (yaEstan.has(i)) continue;

        let ultimo: unknown = null;
        for (let intento = 1; intento <= REINTENTOS; intento++) {
          try {
            await pedir({
              action: "chunk",
              token: sesion.token,
              index: String(i),
              chunk: elegido.slice(i * tam, (i + 1) * tam),
            });
            ultimo = null;
            break;
          } catch (reason) {
            ultimo = reason;
            // Espera creciente: insistir de inmediato con la red caída solo
            // gasta batería.
            if (intento < REINTENTOS) await espera(intento * 1500);
          }
        }
        if (ultimo) throw ultimo;

        hechos += 1;
        setPct(Math.round((hechos / cuantos) * 100));
        setDetalle(`parte ${hechos} de ${cuantos}`);
      }

      return pedir({ action: "complete", token: sesion.token });
    },
    [pedir],
  );

  const subir = useCallback(
    async (elegido: File) => {
      cancelado.current = false;
      setEstado("subiendo");
      setError(null);
      setPct(0);
      setDetalle("Preparando…");

      try {
        const ruta = await pedir({
          action: "direct",
          filename: elegido.name,
          size: String(elegido.size),
        });

        if (ruta.mode === "stream") {
          setModo("stream");
          await aStream(elegido, ruta.uploadUrl, ruta.uid);
          setEstado("listo");
          onDone?.({ videoId: ruta.videoId, name: elegido.name });
          return;
        }

        setModo("fallback");
        const listo = await aNuestro(elegido);
        if (!listo) return;
        setEstado("listo");
        onDone?.(listo);
      } catch (reason) {
        setError(String((reason as Error)?.message ?? reason));
        setEstado("error");
      }
    },
    [pedir, aStream, aNuestro, onDone],
  );

  const limpiar = () => {
    cancelado.current = true;
    subidaTus.current?.abort();
    setFile(null);
    setEstado("idle");
    setModo(null);
    setPct(0);
    setDetalle("");
    setError(null);
  };

  return (
    <div className="flex flex-col gap-3">
      {!file && (
        <label
          className="flex cursor-pointer flex-col items-center gap-2 rounded-lg border border-dashed border-border bg-secondary px-6 py-8 text-center transition-colors hover:border-primary"
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            const soltado = e.dataTransfer.files?.[0];
            if (soltado) {
              setFile(soltado);
              subir(soltado);
            }
          }}
        >
          <CloudUpload className="size-6 text-muted-foreground" aria-hidden="true" />
          <span className="text-sm font-medium text-foreground">
            Arrastrá un video o hacé clic para elegirlo
          </span>
          <span className="text-xs text-muted-foreground">
            Se sube por partes: si se corta el internet, sigue desde donde iba.
          </span>
          <input
            type="file"
            accept="video/*"
            className="sr-only"
            onChange={(event) => {
              const elegido = event.target.files?.[0];
              if (!elegido) return;
              setFile(elegido);
              subir(elegido);
            }}
          />
        </label>
      )}

      {file && (
        <div className="flex flex-col gap-3 rounded-lg border border-border bg-card p-4">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="truncate text-sm font-medium text-foreground">{file.name}</p>
              <p className="flex items-center gap-2 text-xs text-muted-foreground">
                {mb(file.size)}
                {detalle && <>· {detalle}</>}
                {modo && (
                  <Badge variant={modo === "stream" ? "success" : "neutral"}>
                    {modo === "stream" ? "Directo a Cloudflare" : "Almacenamiento propio"}
                  </Badge>
                )}
              </p>
            </div>
            {estado === "listo" ? (
              <CheckCircle2 className="size-5 flex-none text-positive" aria-hidden="true" />
            ) : (
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="size-8"
                aria-label="Cancelar subida"
                onClick={limpiar}
              >
                <X />
              </Button>
            )}
          </div>

          <div className="flex items-center gap-3">
            <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-accent">
              <div
                className={cn(
                  "h-full rounded-full transition-[width]",
                  estado === "error" ? "bg-destructive" : "bg-primary",
                )}
                style={{ width: `${Math.max(pct, 2)}%` }}
                role="progressbar"
                aria-valuenow={pct}
                aria-valuemin={0}
                aria-valuemax={100}
              />
            </div>
            <span className="text-xs tabular-nums text-muted-foreground">{pct}%</span>
          </div>

          {estado === "error" && (
            <Alert variant="destructive">
              <AlertTitle>La subida se cortó</AlertTitle>
              <AlertDescription>
                {error} — lo que ya se subió quedó guardado.
              </AlertDescription>
            </Alert>
          )}

          {(estado === "error" || estado === "pausada") && (
            <Button type="button" size="sm" variant="outline" onClick={() => subir(file)}>
              <RotateCw />
              Reanudar desde donde iba
            </Button>
          )}

          {estado === "listo" && (
            <p className="text-sm text-positive">
              Video subido. Ya está en la biblioteca.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
