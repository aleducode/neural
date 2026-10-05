# Los tokens de `manager.pen`

Contados con [`tokens.py`](tokens.py) sobre los frames 9, 10, 14, 1, 11 y 26, no
mirados. Entre paréntesis, cuántas veces aparece cada uno.

## Color

| Rol | Hex | Dónde |
| --- | --- | --- |
| Superficie / tarjeta | `#ffffff` (343) | fondo de todo widget |
| Texto principal | `#0d0d12` (327) | valores, nombres, item activo del sidebar |
| Texto secundario | `#666d80` (227) | **títulos de widget**, etiquetas, cabeceras de tabla |
| Texto terciario | `#818898` (56) | descripciones, precios |
| Texto cuaternario | `#a4acb9` (25) | títulos de grupo del sidebar |
| Primario | `#22c55e` (79) | caja de icono de KPI, serie 1, logo |
| **Borde** | `#dfe1e7` (481 strokes) | todo `stroke` de widget, tabla y header |
| Separador / relleno | `#eceff3` (51) | badge neutro |
| Superficie suave | `#f6f8fa` (43) | sidebar, cabecera de tabla |
| Superficie oscura | `#121a26` (40) | modo oscuro |
| Positivo | `#28806f` sobre `#ddf3ef` | badge "Paid", delta al alza |
| Negativo | `#b21634` sobre `#fce8ec` | badge de error |
| Negativo fuerte | `#96132c` sobre `#fadbe1` | delta a la baja del KPI |
| Ámbar | `#ffbe4c` (42), texto `#a77b2e`, fondo `#fff9ed` | serie 2, avisos |
| Rampa verde del donut | `#22c55e` → `#6bd893` → `#99e4b5` | tres segmentos |

> `#ffbe4c` **no se usa como color de serie**: contra `#22c55e` da ΔE 4,9 en
> protanopia. Para una marca de datos va `#a77b2e` (ΔE 10,6, pasa todo).
> Ver §6 del SKILL.

## Tipografía

**Inter Tight** en todo el diseño. Ningún otro familia.

| px | lineHeight | peso | uso |
| --- | --- | --- | --- |
| 24 | 1.3 | 600 | título de página, número héroe de la gráfica |
| 20 | 1.35 | 600 | marca del sidebar, total del donut |
| 18 | 1.35 | 600 | valor de KPI |
| 16 | 1.5 | 500 | título de widget, item del sidebar |
| 16 | 1.5 | 400 | subtítulo de página (ls 0.32) |
| 14 | 1.5 | 500 | cabecera de tabla, celda, leyenda (ls 0.28) |
| 14 | 1.5 | 400 | etiqueta de KPI, eje X (ls 0.28) |
| 12 | 1.5 | 500 | badge, botón, delta (ls 0.24; en badge ls 0.12) |
| 12 | 1.5 | 400 | descripción (ls 0.24) |

Pesos: 500 (432), 400 (184), 600 (92). El peso por defecto del diseño es **500**,
no 400.

## Geometría

- **Radios:** 16 (tarjeta, 129), 8 (botón, item de sidebar, 107), 4 (checkbox,
  76), 1000 (avatar, 41), 10 (caja de icono, tooltip, 39), 12 (tarjeta anidada,
  28), 20 (píldora de delta, 23).
- **Gaps:** 8 (296), 10 (193), 2 (102), 4 (88), 6 (66), 16 (42), 12 (28), 24 (20).
- **Paddings:** `[0,12]` celda (243), `[8,12]` item de sidebar (63), `[2,8]`
  badge (62), `[8,16]` botón (32), `[16,16,14,16]` widget de KPI (20),
  `[1,6,1,4]` píldora de delta (23), `[0,20]` cabecera de widget (9).
- **Sombra de widget:** `0 1px 1.75px #0d0d120f`.
- **Sombra de tooltip:** `0 16px 28px #0d0d121a`.
- **Caja de icono del KPI:** 36x36, radio 10, fill `#22c55e`, doble sombra —
  interna `0 -4px 5.25px #ffffff80` y externa `0 1px 1.75px #0d0d121a`. El
  glifo va en **`#0d0d12`**, no en blanco.

## Medidas del chrome

| Pieza | Valor |
| --- | --- |
| Lienzo | 1440x1024 |
| Sidebar expandido | 272, fill `#f6f8fa`, borde derecho 1px |
| Sidebar colapsado | 80 (frame 10) |
| Cabecera del sidebar | 80 de alto, padding `[20,24]` |
| Topbar | 80 de alto, borde inferior 1px, padding `[0,24]` |
| Contenedor | padding 24, gap 24 |
| Cabecera de widget | 64 de alto, borde inferior 1px, padding `[0,20]` |
| Fila de tabla | 64 de alto, borde inferior 1px, padding de fila `[0,9]` |
| Cabecera de tabla | 40 de alto, fill `#f6f8fa` |
| Gráfica de crecimiento | 920x400; área de trazado 806x200 |
| Donut | 372x400, `innerRadius` 0.72 |
| Tabla de transacciones | 916 de ancho |

## El sidebar del diseño

Grupos y items, textuales: **Main Menu** → Dashboard. **Management** → Members,
Trainers, Classes, Bookings. **Operations** → Schedule, Check-in. **Finance** →
Payments, Membership Plans. **Reports & Analytics** → Analytics, Reports. Pie:
Settings, Help & Center, Dark Mode.

Item activo: fill `#0d0d12`, texto `#ffffff`, radio 8. Inactivo: sin fill, texto
`#666d80`.

De todo eso, Neural hoy solo tiene pantallas para Dashboard, socios y
notificaciones. Los demás items **no se implementan** (§3 del SKILL).
