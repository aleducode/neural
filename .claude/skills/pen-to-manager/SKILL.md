---
name: pen-to-manager
description: >-
  Lleva un diseño de Pencil (.pen) al manager de Neural —Django + islas de React
  con shadcn/ui— con fidelidad pixel perfect: vuelca el .pen a texto, mide cada
  token en vez de mirarlo, audita sub-diseño por sub-diseño con agentes en
  paralelo, y aplica la vara de front (datos reales, estados, accesibilidad,
  responsive) sobre lo que el diseño no cubre. Usar cuando el usuario pida
  implementar, extraer, replicar o auditar una pantalla de docs/design/*.pen,
  mencione un frame, un artboard o "pixel perfect".
---

# De Pencil al manager de Neural — implementación pixel perfect

Neural diseña en `docs/design/*.pen` y el manager es **Django + islas de React
con shadcn/ui y Tailwind**, no templates con CSS vanilla y no una SPA. Django
renderiza la página, la autenticación y los datos; React monta dentro de los
`<div data-island>` y recibe props por `json_script`.

Este skill es el camino completo: leer el `.pen`, mapearlo a datos que Neural
realmente tiene, implementarlo, auditarlo y verificarlo contra el navegador.

> Es una adaptación de `pen-to-django` (proyecto hacku, front vanilla). Lo que
> cambia es el destino: acá no se escribe CSS a mano, se escribe contra los
> tokens de `frontend/src/index.css` y los componentes de
> `frontend/src/components/ui/`.

---

## 0. Antes de escribir una línea

**El `.pen` es JSON plano.** `docs/design/manager.pen` abre con `json.load` sin
más: 10,6 MB, 15.210 nodos, 40 frames de 1440x1024. Leerlo con Python es el
camino rápido y no depende de que el editor esté abierto. El MCP de Pencil sirve
para **escribir** en el diseño; para analizar, medir o volcar, el archivo
alcanza y es un orden de magnitud más barato en tokens.

```python
import json, io
d = json.load(io.open('docs/design/manager.pen', encoding='utf-8'))
def n(x): return 1 + sum(n(c) for c in (x.get('children') or []))
for c in d['children']:
    print(f"{n(c):>6}  {c['id']}  «{c.get('name')}»  {c.get('width')}x{c.get('height')}")
```

**Asegurate de que esté commiteado antes de abrirlo en el editor.** Pencil
regraba el archivo con solo tenerlo abierto y puede escribir de vuelta una
generación vieja. Estar commiteado es lo que permite recuperarlo con
`git checkout -- docs/design/manager.pen`.

**Un `.pen` roto no avisa.** El síntoma suele ser solo que el editor no lo abre.
Antes de pelearte con nada:

```bash
python3 -c "import json,io,glob; [json.load(io.open(f,encoding='utf-8')) for f in glob.glob('docs/design/*.pen')]"
```

**Lee el diseño entero antes de tocar el front.** No el frame que te pidieron:
los estados de error, los vacíos y las variantes viven en frames hermanos
(`2. Sign In - Error State`, `13. Search - Empty`), y son justo lo que se pierde.

**Mira qué existe ya.** Antes de crear un token o un componente, buscá si el
proyecto ya lo tiene:

```bash
grep -n -- "--[a-z-]*:" frontend/src/index.css
ls frontend/src/components/ui/
```

Duplicar un token es cómo se desincronizan.

---

## 1. Volcar el diseño a texto

El árbol de un frame no entra en una respuesta: se aplana a un archivo y se
trabaja con `grep` y rangos de línea. El volcado vive en `docs/design/dump/`
(no se commitea: es derivado).

```python
import json, io
data = json.load(io.open('docs/design/manager.pen', encoding='utf-8'))
idx = {c['id']: c for c in data['children']}

def dump(node, path):
    out = []
    def walk(n, d=0):
        props = {k: v for k, v in n.items() if k not in ('children', 'type', 'id', 'name')}
        line = '  ' * d + f"{n.get('type')} #{n.get('id')} «{n.get('name','')}»"
        if 'content' in props:
            line += f"  TEXT={json.dumps(props.pop('content'), ensure_ascii=False)}"
        if props:
            line += '  ' + json.dumps(props, ensure_ascii=False)
        out.append(line)
        for c in n.get('children') or []:
            walk(c, d + 1)
    walk(node)
    io.open(path, 'w', encoding='utf-8').write('\n'.join(out))

dump(idx['FZjwU'], 'docs/design/dump/10-dashboard.txt')
```

El esqueleto, para ubicar cada sub-diseño y sus rangos de línea:

```bash
awk '{ match($0,/^ */); d=RLENGTH/2; if (d<=4) { line=$0; sub(/  \{.*/,"",line); print NR": "line } }' \
  docs/design/dump/10-dashboard.txt
```

Todas las cadenas, para no inventar ninguna:

```bash
grep -n 'TEXT=' docs/design/dump/10-dashboard.txt | sed 's/  {.*//'
```

**Cada frame repite el sidebar y el topbar completos.** Solo interesa el frame
de contenido; las ~80 líneas de sidebar son ruido una vez que el chrome está
hecho.

**Los tokens salen contados, no mirados.** Hay un script que inventaría fills,
strokes, radios, tamaños y pesos sobre los frames que le pases:
[`references/tokens.py`](references/tokens.py). El token real es el que más se
repite, no el que te llamó la atención. Los de `manager.pen` ya están resueltos
en [`references/design-tokens.md`](references/design-tokens.md).

---

## 2. Traducir el lienzo a la pantalla real

El diseño trabaja sobre un lienzo fijo de 1440 (sidebar 272 + main 1168, o
sidebar colapsado 80 + main 1360). Traducirlo literal rompe:

| En el diseño | En el front |
| --- | --- |
| `width: 920` y `width: "fill_container"` lado a lado | `grid-cols-[1fr_380px]` o `flex-1` + `w-[372px]`, nunca anchos fijos en los dos |
| `padding: 24` sobre el contenedor raíz | `p-6` en el `<main>`, no en cada tarjeta |
| `gap`, `cornerRadius`, `fontSize`, `strokeWidth` | literal, son valores absolutos |
| `textGrowth: "fixed-width"` | el texto **envuelve** — nada de `whitespace-nowrap` |
| `textGrowth: "auto"` | el texto nunca envuelve |
| `enabled: false` | el nodo está **oculto**: es un resto del diseño, no se implementa |
| `height: 400` en una tarjeta | `h-[400px]` solo si el contenido es fijo; si es una lista, `min-h` |
| `effect: shadow` | un `shadow-*` propio en `tailwind.config`, no el `shadow-sm` genérico |

`enabled: false` aparece mucho: botones de chevron apagados, badges de ejemplo
(`"Label"`, `"+4"`), fondos de debug. **Grep antes de implementar un nodo:**

```bash
grep -c '"enabled": false' docs/design/dump/10-dashboard.txt
```

Si el diseño usa una librería de iconos que el proyecto no carga, **decilo y
decidí explícitamente** — el manager usa `lucide-react`; no dibujes el glifo a
mano, queda mal siempre.

---

## 3. Los datos mandan sobre el diseño

Esta es la regla que más plata ahorra y la que más se rompe.

Los `.pen` traen cifras y personas inventadas: `"1,284"`, `"$32,450"`,
`"Siti Rahma"`, `"Bank Transfer"`, `"18 Active Trainers"`. **Nada de eso se
copia.** El layout se copia; el dato se saca de Neural.

Antes de implementar un widget, buscá el modelo que lo alimenta:

```bash
grep -n "^class \|^    [a-z_]* = models\." neural/users/models.py neural/training/models.py
```

Para cada widget del diseño, una de tres:

1. **Hay dato real** → se mapea y se implementa. Es el caso normal.
2. **Hay dato parecido** → se implementa con el dato real y se **renombra la
   etiqueta** para que diga la verdad. "Payment Method" sin medio de pago
   guardado se convierte en "Plan", que sí existe.
3. **No hay dato** → el widget **no se implementa** y se reporta como hueco de
   producto. No se inventa, no se deja en cero, no se pone "próximamente".

Prometer en la interfaz algo que el backend no hace es el peor resultado posible
de este trabajo. Lo mismo con el registro: si el diseño está en inglés y el
producto habla español de Colombia, manda el producto.

**Nada de controles muertos.** Si el diseño dibuja un buscador, un filtro
"Monthly" o un menú `…` y no hay nada detrás, no se pone: un control que no hace
nada es peor que su ausencia. O se implementa de verdad, o se reporta.

---

## 4. Las trampas que ya nos costaron caro en este repo

Cada una rompió algo en producción o en QA. Están primero porque son las que no
se ven revisando el código.

### `{# #}` es de una sola línea

Django corta el comentario en el primer salto de línea: un `{# #}` de tres
líneas renderiza las dos últimas **como texto visible en la página**. Nos pasó
en `manager/base.html` y salió a producción. Para varias líneas,
`{% comment %}…{% endcomment %}`.

### `preflight: false` deja el panel con viñetas

Apagar `corePlugins.preflight` en `tailwind.config` para no pisar el CSS viejo
deja listas con viñetas y enlaces subrayados en todo el manager. El manager ya
no comparte CSS con el resto: **preflight va encendido**.

### `json_script` escapa, `|safe` no

Las props de una isla viajan con `{{ props|json_script:"id-props" }}`. Un
`|safe` sobre el mismo JSON es un XSS esperando un nombre de socio con `<`.

### Una isla que falla deja la página en blanco

`main.tsx` tiene un `revealContent()` con timeout y listener de `error` para que
un fallo de montaje muestre el HTML de Django en vez de nada. Si agregás una
isla, no la montes fuera de ese camino.

### El bundle tiene nombres fijos

`vite.config.ts` escribe nombres sin hash en
`neural/manager/static/manager/bundle/` porque el template los referencia
directo. Si cambiás el nombre de un entry, actualizá el template.

### `docker compose exec` no carga el `env_file`

Solo `run --rm` lo hace, pero `run --rm` no tiene el manifest de collectstatic.
Para verificar estáticos, comprobá el manifest directamente.

### Botones que son `<a>`

Un `<a>` con `asChild` dentro de un `<Button>` hereda el `a:hover` global.
Fijá `text-decoration` y `color` por variante en `:hover`, `:focus` y `:active`.

---

## 5. Lo que el diseño no dice y hay que poner igual

Un `.pen` dibuja el camino feliz a un ancho fijo. Lo demás es nuestro. La vara
completa, con el porqué de cada punto, está en
[`references/frontend-bar.md`](references/frontend-bar.md). El resumen:

- **Estados que faltan:** vacío, cargando, error, parcial, sin permiso.
- **Foco visible** en todo control, incluidos los `<a>` disfrazados de botón.
- **Semántica.** Una tabla con `div` necesita `role`; usá `<table>` si podés.
- **Responsive.** El lienzo es 1440: definí qué colapsa, qué se apila y qué
  scrollea. Probá a ~400px antes de dar nada por terminado.
- **Gráficas:** el skill `dataviz` manda sobre el `.pen`. **El validador se
  corre, no se razona** (ver §6).
- **Español de Colombia** en toda cadena visible. El manager no tiene i18n: el
  texto va directo en español, no en inglés con `{% trans %}`.

---

## 6. Las gráficas se validan, no se miran

El `.pen` elige colores por gusto. El skill `dataviz` tiene un validador que
mide separación para daltonismo, banda de luminosidad y contraste:

```bash
node <skill dataviz>/scripts/validate_palette.js "#22c55e,#ffbe4c" --mode light
```

**Esto ya pasó con `manager.pen`:** la pareja verde + ámbar de la gráfica de
crecimiento da ΔE 4,9 en protanopia — por debajo incluso del piso de 6. La
corrección mínima y fiel al diseño es usar `#a77b2e`, que es **un token del
propio diseño** (el ámbar de texto) y pasa todos los chequeos con ΔE 10,6.

Reglas que no se negocian, aunque el diseño haga otra cosa:

- Nunca doble eje. Dos medidas de escala distinta son dos gráficas.
- Secuencial = un solo hue, claro → oscuro. Nunca arcoíris.
- Leyenda siempre que haya ≥2 series; ninguna si hay una sola (el título la
  nombra).
- El texto lleva tokens de texto, nunca el color de la serie.
- Un WARN de contraste obliga a etiquetas visibles o vista de tabla. No se
  descarta.

Cuando el diseño y el validador chocan, gana el validador y **se reporta la
diferencia**, no se aplica en silencio.

---

## 7. La auditoría pixel perfect

Una vez implementado, **un agente por sub-diseño, todos en paralelo, todos de
solo lectura.** Los hallazgos los aplica una sola mano en secuencia: varios
agentes editando el mismo `.tsx` se pisan.

Más un agente aparte para el **chrome compartido** (sidebar, topbar), porque
cambia entre variantes —expandido 272 vs colapsado 80— y es donde más detalle
se pierde.

El prompt está en [`references/audit-prompt.md`](references/audit-prompt.md).

---

## 8. Verificar contra el navegador, no contra el ojo

El preview local corre en `http://localhost:5174` (`npm run dev:preview` en
`frontend/`, rutas reales: `/dashboard`, `/usuarios`, `/notificaciones`).

```bash
npx tsc --noEmit
npx vite build
```

Y en el navegador, con valores computados:

```js
getComputedStyle(el).padding
el.getBoundingClientRect()                       // ¿272 el sidebar? ¿64 la fila?
[...document.querySelectorAll('svg')].map(s => s.getBoundingClientRect().width)
```

Playwright a 1440x1024 contra el frame del `.pen` lado a lado es lo único que
encuentra las diferencias de 2px.

**No se despliega sin permiso explícito.** Todo se prueba en local primero; el
usuario decide cuándo sale.

---

## 9. Hallazgos que se repiten

- Nodos con `enabled: false` implementados como si existieran (badges "Label",
  "+4", chevrons apagados).
- Datos de utilería del `.pen` copiados tal cual en vez de mapeados.
- Controles dibujados sin nada detrás (buscador, filtro "Monthly", menú `…`).
- Iconos genéricos donde el diseño pide uno específico, y tamaños que vuelven
  a 24px porque la regla se escribió contra el nodo equivocado.
- Títulos de tarjeta en `#666d80` implementados en color de texto principal:
  en este diseño el título de widget **es** secundario, a propósito.
- El borde: el diseño usa `#dfe1e7` para stroke y `#eceff3` para relleno de
  separadores. No son el mismo token.
