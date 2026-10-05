/**
 * Ingresos por plan.
 *
 * Es una particion de un total, no categorias independientes: un solo hue en
 * tres pasos, de mas a menos, como en el .pen (#22c55e / #6bd893 / #99e4b5).
 * Los pasos salen de --donut-N, que el modo oscuro vuelve a elegir contra
 * #121a26 en vez de invertir.
 *
 * Cada segmento lleva su etiqueta y su cifra en la leyenda: el color no es la
 * unica manera de saber cual es cual.
 */

export type Segment = {
  id: number | null;
  label: string;
  value: number;
  share: number;
  amount: string;
};

type Props = {
  segments: Segment[];
  total: string;
  period: string;
};

const SIZE = 232;
const STROKE = 32; // innerRadius 0.72 sobre un radio de 116
const R = (SIZE - STROKE) / 2;
const C = 2 * Math.PI * R;

export default function RevenueDonut({ segments, total, period }: Props) {
  const sum = segments.reduce((acc, s) => acc + s.value, 0);

  if (!sum) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-2 px-6 py-10 text-center">
        <p className="text-sm font-medium text-foreground">Sin ingresos registrados</p>
        <p className="text-sm text-muted-foreground">
          Todavía no hay pagos confirmados en los {period}.
        </p>
      </div>
    );
  }

  let offset = 0;
  const arcs = segments.map((segment, i) => {
    const length = (segment.value / sum) * C;
    // 2px de aire entre segmentos para que dos pasos vecinos no se peguen.
    const arc = { ...segment, length: Math.max(length - 2, 1), offset, step: i };
    offset += length;
    return arc;
  });

  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-6 px-5 py-5">
      <div className="relative" style={{ width: SIZE, height: SIZE }}>
        <svg width={SIZE} height={SIZE} role="img" aria-label={`Ingresos por plan, ${period}`}>
          <g transform={`rotate(-90 ${SIZE / 2} ${SIZE / 2})`}>
            {arcs.map((arc) => (
              <circle
                key={`${arc.id}-${arc.label}`}
                cx={SIZE / 2}
                cy={SIZE / 2}
                r={R}
                fill="none"
                stroke={`var(--donut-${Math.min(arc.step + 1, 3)})`}
                strokeWidth={STROKE}
                strokeDasharray={`${arc.length} ${C - arc.length}`}
                strokeDashoffset={-arc.offset}
              >
                <title>{`${arc.label}: ${arc.amount} (${arc.share}%)`}</title>
              </circle>
            ))}
          </g>
        </svg>

        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center gap-0.5">
          <span className="text-xs font-medium text-faint">Total recaudado</span>
          <span className="text-xl font-semibold tabular-nums text-foreground">{total}</span>
        </div>
      </div>

      <ul className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2">
        {arcs.map((arc) => (
          <li key={`${arc.id}-${arc.label}-legend`} className="flex items-center gap-2">
            <span
              className="size-2.5 flex-none rounded-full"
              style={{ background: `var(--donut-${Math.min(arc.step + 1, 3)})` }}
              aria-hidden="true"
            />
            <span className="text-sm font-medium text-foreground">{arc.label}</span>
            <span className="text-sm tabular-nums text-muted-foreground">{arc.share}%</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
