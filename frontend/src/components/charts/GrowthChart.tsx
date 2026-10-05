import { useLayoutEffect, useRef, useState } from "react";

/**
 * Crecimiento de usuarios, dos series sobre un solo eje.
 *
 * Las dos series son personas: misma unidad, misma escala, un solo eje. Nada
 * de doble eje, que es el error numero uno de este tipo de grafica.
 *
 * El .pen pinta la segunda serie en #ffbe4c. Contra el verde da ΔE 4,9 en
 * protanopia, por debajo del piso de 6, asi que va #a77b2e --el ambar de texto
 * del propio diseño-- que pasa con ΔE 10,6. Los dos salen de --series-N.
 */

export type GrowthPoint = { label: string; newUsers: number; activeUsers: number };
export type GrowthSeries = { key: "newUsers" | "activeUsers"; label: string };

type Props = {
  points: GrowthPoint[];
  series: GrowthSeries[];
};

const PAD = { top: 12, right: 8, bottom: 0, left: 0 };
const MIN_H = 200;

/** Ticks redondos que cubren el maximo sin pasarse de cinco. */
function ticksFor(max: number) {
  if (max <= 0) return [0, 1];
  const raw = max / 4;
  const mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= raw) ?? mag * 10;
  const top = Math.ceil(max / step) * step;
  const out: number[] = [];
  for (let v = 0; v <= top + 1e-9; v += step) out.push(Math.round(v));
  return out;
}

/** Curva monotona: pasa por cada punto y no inventa picos entre ellos. */
function smoothPath(xs: number[], ys: number[]) {
  if (xs.length < 2) return "";
  const n = xs.length;
  const d: string[] = [`M${xs[0]},${ys[0]}`];
  for (let i = 0; i < n - 1; i++) {
    const x0 = xs[i === 0 ? 0 : i - 1];
    const y0 = ys[i === 0 ? 0 : i - 1];
    const x1 = xs[i];
    const y1 = ys[i];
    const x2 = xs[i + 1];
    const y2 = ys[i + 1];
    const x3 = xs[i + 2 < n ? i + 2 : n - 1];
    const y3 = ys[i + 2 < n ? i + 2 : n - 1];
    const c1x = x1 + (x2 - x0) / 6;
    const c1y = y1 + (y2 - y0) / 6;
    const c2x = x2 - (x3 - x1) / 6;
    const c2y = y2 - (y3 - y1) / 6;
    d.push(`C${c1x},${c1y} ${c2x},${c2y} ${x2},${y2}`);
  }
  return d.join(" ");
}

export default function GrowthChart({ points, series }: Props) {
  const box = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ width: 0, height: MIN_H });
  const [hover, setHover] = useState<number | null>(null);

  useLayoutEffect(() => {
    const node = box.current;
    if (!node) return;
    const observer = new ResizeObserver(([entry]) =>
      setSize({ width: entry.contentRect.width, height: entry.contentRect.height }),
    );
    observer.observe(node);
    const rect = node.getBoundingClientRect();
    setSize({ width: rect.width, height: rect.height });
    return () => observer.disconnect();
  }, []);

  if (points.length < 2) {
    return (
      <p className="px-5 py-10 text-center text-sm text-muted-foreground">
        Hacen falta al menos dos meses de historia para dibujar la tendencia.
      </p>
    );
  }

  const max = Math.max(...points.flatMap((p) => [p.newUsers, p.activeUsers]), 1);
  const ticks = ticksFor(max);
  const top = ticks[ticks.length - 1];

  // La grafica ocupa lo que la fila le de: asi las dos tarjetas de la fila
  // terminan a la misma altura sin recortar nada.
  const { width } = size;
  const plotH = Math.max(size.height, MIN_H);
  const plotW = Math.max(width - PAD.left - PAD.right, 1);
  const x = (i: number) => PAD.left + (i / (points.length - 1)) * plotW;
  const y = (v: number) => PAD.top + (1 - v / top) * (plotH - PAD.top);

  const xs = points.map((_, i) => x(i));
  const lines = series.map((s) => ({
    ...s,
    path: smoothPath(xs, points.map((p) => y(p[s.key]))),
    color: s.key === "newUsers" ? "var(--series-1)" : "var(--series-2)",
  }));

  const area = `${lines[0].path} L${xs[xs.length - 1]},${plotH} L${xs[0]},${plotH} Z`;
  const active = hover;
  // Cada etiqueta de mes necesita ~32px. Si no caben todas, se muestra una de
  // cada N en vez de dejar que se peguen («NovDicEneFeb...»).
  const stride = Math.max(1, Math.ceil(points.length / Math.max(Math.floor(plotW / 32), 1)));

  return (
    <div className="flex flex-1 flex-col gap-4 px-5 pb-5 pt-2">
      <div className="flex min-h-[200px] flex-1 gap-8">
        {/* Eje Y: cada etiqueta sobre su propia linea de rejilla, no repartidas
            a ojo por el alto del contenedor. */}
        <div className="relative w-7 flex-none" aria-hidden="true">
          {ticks.map((tick) => (
            <span
              key={tick}
              className="absolute right-0 -translate-y-1/2 text-xs tabular-nums text-muted-foreground"
              style={{ top: y(tick) }}
            >
              {tick}
            </span>
          ))}
        </div>

        <div className="relative min-w-0 flex-1" ref={box}>
          {width > 0 && (
            <svg
              width={width}
              height={plotH}
              className="absolute inset-0 block overflow-visible"
              role="img"
              aria-label={`Usuarios nuevos y usuarios que entrenaron, ${points[0].label} a ${points[points.length - 1].label}`}
              onMouseLeave={() => setHover(null)}
            >
              <defs>
                <linearGradient id="growth-area" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--series-1)" stopOpacity="0.22" />
                  <stop offset="100%" stopColor="var(--series-1)" stopOpacity="0" />
                </linearGradient>
              </defs>

              {/* Rejilla vertical: una por mes, recesiva */}
              {xs.map((cx, i) => (
                <line
                  key={i}
                  x1={cx}
                  x2={cx}
                  y1={0}
                  y2={plotH}
                  stroke="currentColor"
                  strokeWidth="1"
                  className="text-border"
                />
              ))}

              <path d={area} fill="url(#growth-area)" />

              {lines.map((line) => (
                <path
                  key={line.key}
                  d={line.path}
                  fill="none"
                  stroke={line.color}
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              ))}

              {active !== null && (
                <line
                  x1={xs[active]}
                  x2={xs[active]}
                  y1={0}
                  y2={plotH}
                  stroke="currentColor"
                  strokeWidth="1"
                  className="text-foreground/25"
                />
              )}

              {/* Marcas: anillo de la superficie para que no se fundan con la
                  linea. 8px, no los 4,68 del .pen: por debajo de 8 el punto
                  deja de ser un objetivo de mouse. */}
              {lines.map((line) =>
                points.map((p, i) => (
                  <circle
                    key={`${line.key}-${i}`}
                    cx={xs[i]}
                    cy={y(p[line.key])}
                    r={active === i ? 5 : 4}
                    fill={line.color}
                    stroke="var(--viz-surface)"
                    strokeWidth="2"
                  />
                )),
              )}

              {/* Zonas de hover mas anchas que la marca */}
              {points.map((p, i) => (
                <rect
                  key={`hit-${i}`}
                  x={xs[i] - plotW / (points.length - 1) / 2}
                  y={0}
                  width={plotW / (points.length - 1)}
                  height={plotH}
                  fill="transparent"
                  onMouseEnter={() => setHover(i)}
                >
                  <title>{`${p.label}: ${p.newUsers} nuevos, ${p.activeUsers} entrenaron`}</title>
                </rect>
              ))}
            </svg>
          )}

          {active !== null && width > 0 && (
            <div
              className="pointer-events-none absolute z-10 w-36 -translate-x-1/2 rounded-[10px] border border-border bg-popover px-3 py-2.5 shadow-pop"
              style={{
                left: Math.min(Math.max(xs[active], 72), width - 72),
                top: 8,
              }}
            >
              <div className="text-xs font-semibold uppercase text-foreground">
                {points[active].label}
              </div>
              <dl className="mt-2 flex flex-col gap-1">
                {lines.map((line) => (
                  <div key={line.key} className="flex items-center justify-between gap-4">
                    <dt className="text-xs text-muted-foreground">{line.label}</dt>
                    <dd
                      className="text-xs font-semibold tabular-nums"
                      style={{ color: line.color }}
                    >
                      {points[active][line.key]}
                    </dd>
                  </div>
                ))}
              </dl>
            </div>
          )}
        </div>
      </div>

      {/* Mismo esqueleto que la fila de arriba (columna de 28 + gap de 32) para
          que los meses caigan bajo su punto y no 18px corridos. */}
      <div className="flex gap-8 text-sm text-muted-foreground" aria-hidden="true">
        <span className="w-7 flex-none" />
        <div className="flex min-w-0 flex-1 justify-between">
          {points.map((p, i) => (
            <span key={i} className={i % stride === 0 ? undefined : "invisible"}>
              {p.label}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
