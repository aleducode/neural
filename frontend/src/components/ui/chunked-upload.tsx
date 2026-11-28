import { CheckCircle2, CloudUpload, RotateCw, X } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import * as tus from "tus-js-client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

/**
 * Video uploads, built for bad internet and for many files at once.
 *
 * The server picks the route for each file, not the browser:
 *  - `stream`: Cloudflare hands out a one-time URL and the file goes straight
 *    there over tus. It never passes through Django. Resumable by the protocol.
 *  - `fallback`: no Cloudflare token, so chunks go to our own storage. Also
 *    resumable, by asking which parts already arrived.
 *
 * Every file is its own upload with its own progress; the queue only decides
 * how many run at the same time.
 */

const CHUNK = 5 * 1024 * 1024; // 5 MB: the smallest part Cloudflare accepts
const RETRIES = 3;
// Three at once keeps a gym's connection usable; more only splits the same
// bandwidth into slower uploads.
const PARALLEL = 3;

export type UploadStatus = "queued" | "uploading" | "done" | "error";
export type QueuedFile = { key: string; file: File; status: UploadStatus };

const wait = (ms: number) => new Promise((r) => setTimeout(r, ms));
const mb = (bytes: number) => `${(bytes / (1024 * 1024)).toFixed(1)} MB`;

/** The queue lives in the page, so uploads keep going with the dialog closed. */
export function useUploadQueue() {
  const [items, setItems] = useState<QueuedFile[]>([]);

  const add = useCallback((files: File[]) => {
    const videos = files.filter((f) => f.type.startsWith("video/"));
    setItems((current) => [
      ...current,
      ...videos.map((file) => ({
        key: `${file.name}-${file.size}-${file.lastModified}-${Math.random()}`,
        file,
        status: "queued" as const,
      })),
    ]);
    return videos.length;
  }, []);

  const setStatus = useCallback((key: string, status: UploadStatus) => {
    setItems((current) => current.map((i) => (i.key === key ? { ...i, status } : i)));
  }, []);

  const remove = useCallback((key: string) => {
    setItems((current) => current.filter((i) => i.key !== key));
  }, []);

  const clear = useCallback(() => setItems([]), []);

  // A file starts when it is among the first PARALLEL still pending. A failed
  // one gives up its slot until someone retries it.
  const pending = items.filter((i) => i.status === "queued" || i.status === "uploading");
  const active = new Set(pending.slice(0, PARALLEL).map((i) => i.key));
  const done = items.filter((i) => i.status === "done").length;
  const failed = items.filter((i) => i.status === "error").length;

  // Closing the tab mid-upload loses whatever was not sent: warn first.
  const busy = pending.length > 0;
  useEffect(() => {
    if (!busy) return;
    const warn = (event: BeforeUnloadEvent) => event.preventDefault();
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [busy]);

  return { items, add, setStatus, remove, clear, active, busy, done, failed };
}

export function DropZone({ onFiles }: { onFiles: (files: File[]) => void }) {
  return (
    <label
      className="flex cursor-pointer flex-col items-center gap-2 rounded-lg border border-dashed border-border bg-secondary px-6 py-8 text-center transition-colors hover:border-primary"
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => {
        e.preventDefault();
        onFiles(Array.from(e.dataTransfer.files ?? []));
      }}
    >
      <CloudUpload className="size-6 text-muted-foreground" aria-hidden="true" />
      <span className="text-sm font-medium text-foreground">
        Arrastrá los videos o hacé clic para elegirlos
      </span>
      <span className="text-xs text-muted-foreground">
        Podés elegir varios. Se suben de a {PARALLEL} y, si se corta el internet,
        siguen desde donde iban.
      </span>
      <input
        type="file"
        accept="video/*"
        multiple
        className="sr-only"
        onChange={(event) => {
          onFiles(Array.from(event.target.files ?? []));
          event.target.value = "";
        }}
      />
    </label>
  );
}

/** One file's upload. It starts on its own once the queue makes it active. */
export function UploadRow({
  uploadUrl,
  csrfToken,
  item,
  active,
  onStatus,
  onRemove,
}: {
  uploadUrl: string;
  csrfToken: string;
  item: QueuedFile;
  active: boolean;
  onStatus: (status: UploadStatus) => void;
  onRemove: () => void;
}) {
  const { file, status } = item;
  const [pct, setPct] = useState(0);
  const [detail, setDetail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const cancelled = useRef(false);
  const tusUpload = useRef<tus.Upload | null>(null);

  const request = useCallback(
    async (fields: Record<string, string | Blob>) => {
      const body = new FormData();
      body.append("csrfmiddlewaretoken", csrfToken);
      for (const [k, v] of Object.entries(fields)) body.append(k, v);
      const response = await fetch(uploadUrl, { method: "POST", body });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error ?? `Error ${response.status}`);
      return data;
    },
    [uploadUrl, csrfToken],
  );

  /** Straight to Cloudflare with tus: it resumes and retries by itself. */
  const toStream = useCallback(
    (destination: string, uid: string) =>
      new Promise<void>((resolve, reject) => {
        const upload = new tus.Upload(file, {
          uploadUrl: destination,
          chunkSize: CHUNK,
          retryDelays: [0, 3000, 6000, 12000],
          metadata: { name: file.name, filetype: file.type },
          onProgress: (sent, total) => {
            setPct(Math.round((sent / total) * 100));
            setDetail(`${mb(sent)} de ${mb(total)}`);
          },
          onError: reject,
          onSuccess: async () => {
            // The bytes arrived but Cloudflare is still encoding, so the
            // duration and "ready" do not exist yet. Ask a few times; if that
            // is not enough, `sync_stream_videos` picks it up later.
            for (let attempt = 0; attempt < 6; attempt++) {
              setDetail("Procesando en Cloudflare…");
              const state = await request({ action: "confirm", uid });
              if (state.ready) {
                setDetail(`Listo · ${Math.round(state.duration)} s`);
                break;
              }
              await wait(5000);
            }
            resolve();
          },
        });
        tusUpload.current = upload;
        upload.start();
      }),
    [file, request],
  );

  /** To our own storage, asking which parts already arrived. */
  const toOwnStorage = useCallback(async () => {
    const session = await request({
      action: "init",
      filename: file.name,
      size: String(file.size),
      chunkSize: String(CHUNK),
    });
    const size: number = session.chunkSize;
    const total: number = session.totalChunks;
    const already = new Set<number>(session.received ?? []);
    let sent = already.size;
    setPct(Math.round((sent / total) * 100));

    for (let i = 0; i < total; i++) {
      if (cancelled.current) return false;
      if (already.has(i)) continue;

      let last: unknown = null;
      for (let attempt = 1; attempt <= RETRIES; attempt++) {
        try {
          await request({
            action: "chunk",
            token: session.token,
            index: String(i),
            chunk: file.slice(i * size, (i + 1) * size),
          });
          last = null;
          break;
        } catch (reason) {
          last = reason;
          // Back off: hammering a dead network only drains the battery.
          if (attempt < RETRIES) await wait(attempt * 1500);
        }
      }
      if (last) throw last;

      sent += 1;
      setPct(Math.round((sent / total) * 100));
      setDetail(`parte ${sent} de ${total}`);
    }

    await request({ action: "complete", token: session.token });
    return true;
  }, [file, request]);

  const start = useCallback(async () => {
    cancelled.current = false;
    onStatus("uploading");
    setError(null);
    setDetail("Preparando…");

    try {
      const route = await request({
        action: "direct",
        filename: file.name,
        size: String(file.size),
      });
      if (route.mode === "stream") {
        await toStream(route.uploadUrl, route.uid);
      } else if (!(await toOwnStorage())) {
        return;
      }
      setPct(100);
      onStatus("done");
    } catch (reason) {
      if (cancelled.current) return;
      setError(String((reason as Error)?.message ?? reason));
      onStatus("error");
    }
  }, [file, request, toStream, toOwnStorage, onStatus]);

  // Runs once per turn in the queue; a retry calls `start` directly.
  useEffect(() => {
    if (active && status === "queued") start();
  }, [active, status, start]);

  // Removing the row or leaving the page stops its transfer.
  useEffect(
    () => () => {
      cancelled.current = true;
      tusUpload.current?.abort();
    },
    [],
  );

  return (
    <li className="flex flex-col gap-2 py-3">
      <div className="flex items-center justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-foreground">{file.name}</p>
          <p className="text-xs text-muted-foreground">
            {mb(file.size)}
            {status === "queued" && " · En espera"}
            {status !== "queued" && detail && ` · ${detail}`}
          </p>
        </div>
        {status === "done" ? (
          <CheckCircle2 className="size-5 flex-none text-positive" aria-label="Subido" />
        ) : status === "error" ? (
          <span className="flex flex-none items-center gap-1">
            <Button type="button" variant="outline" size="sm" onClick={start}>
              <RotateCw />
              Reintentar
            </Button>
            <Button type="button" variant="ghost" size="icon" className="size-8" aria-label={`Quitar ${file.name}`} onClick={onRemove}>
              <X />
            </Button>
          </span>
        ) : (
          <Button type="button" variant="ghost" size="icon" className="size-8 flex-none" aria-label={`Cancelar ${file.name}`} onClick={onRemove}>
            <X />
          </Button>
        )}
      </div>
      {status !== "done" && (
        <div className="flex items-center gap-3">
          <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-accent">
            <div
              className={cn(
                "h-full rounded-full transition-[width]",
                status === "error" ? "bg-destructive" : "bg-primary",
              )}
              style={{ width: `${Math.max(pct, status === "queued" ? 0 : 2)}%` }}
              role="progressbar"
              aria-valuenow={pct}
              aria-valuemin={0}
              aria-valuemax={100}
            />
          </div>
          <span className="w-9 text-right text-xs tabular-nums text-muted-foreground">{pct}%</span>
        </div>
      )}
      {error && (
        <p className="text-xs text-destructive">
          {error}. Lo que ya se subió quedó guardado.
        </p>
      )}
    </li>
  );
}
