# El prompt de auditoría

Uno por sub-diseño, todos lanzados en la misma respuesta para que corran en
paralelo. Todos de **solo lectura**: el entregable es una lista de hallazgos, no
un diff.

Los rangos de línea salen del volcado (`docs/design/dump/*.txt`). Dárselos al
agente evita que tenga que abrir el `.pen` de 10 MB.

Reemplazar lo que está entre `<>`.

---

> Eres un ingeniero de front senior haciendo una auditoría **pixel-perfect** de
> una pantalla ya implementada contra su diseño. **No edites ningún archivo:**
> tu entregable es una lista de hallazgos que aplica otra persona.
>
> **Diseño (fuente de verdad):** `<ARCHIVO_DUMP>`, líneas `<A>`–`<B>`,
> sub-diseño «`<NOMBRE>`». Es un volcado del `.pen`: cada nodo trae su tipo, su
> nombre, su texto y todas sus propiedades (`fill`, `cornerRadius`, `stroke`,
> `strokeWidth`, `gap`, `padding`, `fontSize`, `fontWeight`, `lineHeight`,
> `letterSpacing`, `width`, `height`, `effect`). Léelo **entero**, línea por
> línea.
>
> **Implementación:**
> - `<ISLA .tsx>`
> - `<COMPONENTES ui/ y charts/ que usa>`
> - `<VISTA Django que arma las props>`
> - Tokens: `frontend/src/index.css`, `frontend/tailwind.config.js`
>
> Compara **nodo por nodo**, de arriba hacia abajo, sin saltarte ninguno.
> Para cada nodo del diseño verifica:
>
> 1. **Existe.** Si no está en el front, es un hallazgo, aunque parezca menor
>    (un divisor, un contador, un estado vacío). **Excepción:** un nodo con
>    `"enabled": false` está oculto en el diseño y **no debe** estar en el
>    front; si está, eso también es un hallazgo.
> 2. **El icono es el mismo.** Nombre exacto de `lucide-react` y tamaño exacto.
>    Si el diseño usa una librería que el proyecto no carga, dilo explícitamente
>    en vez de dejarlo pasar.
> 3. **El texto es el mismo** — salvo que sea dato de utilería. El diseño está
>    en inglés y con cifras inventadas (`"1,284"`, `"Siti Rahma"`, `"$32,450"`).
>    El manager va en español de Colombia y con datos de Neural: lo que se
>    audita ahí es que la **etiqueta diga la verdad sobre el dato que muestra**,
>    no que diga lo mismo que el `.pen`. Una etiqueta que promete un dato que el
>    backend no produce es un hallazgo GRAVE.
> 4. **Los valores son los mismos.** `padding`, `gap`, `fontSize`, `fontWeight`,
>    `lineHeight`, `letterSpacing`, `cornerRadius`, `stroke`, `strokeWidth`,
>    `fill`, `width`, `height`, `effect`. Reporta el valor del diseño y el de
>    la clase de Tailwind, convertido a px.
> 5. **La estructura es la misma.** Orden de los hijos, dirección del layout,
>    alineación, qué está en la misma fila y qué no.
>
> Verifica también lo que el diseño **no** dice pero la pantalla necesita:
> estados vacío, cargando, error y sin permiso; textos que se cortan;
> `:focus-visible` en cada control; semántica de tabla; y qué pasa a ~400px de
> ancho.
>
> **Reglas del proyecto:** el manager no tiene i18n, el texto va en español
> directo. Identificadores y comentarios siguen el estilo del archivo que estás
> auditando. Ningún control que no haga nada. Ninguna cifra inventada.
>
> **Entrega** una lista ordenada por gravedad. Cada hallazgo, en este formato:
>
> ```
> [GRAVE|MEDIO|MENOR] <archivo>:<línea> — <qué está mal>
>   Diseño:  <valor/texto/icono exacto del .pen, con el id del nodo>
>   Front:   <lo que hay hoy>
>   Arreglo: <el cambio concreto: la clase de Tailwind o el JSX>
> ```
>
> GRAVE = falta un elemento o un estado entero, o la pantalla promete un dato
> que no existe.
> MEDIO = icono, texto o valor equivocado que se nota a simple vista.
> MENOR = diferencia de 1-2px o un token que nadie va a ver pero conviene fijar.
>
> No propongas rediseños ni mejoras: solo la diferencia contra el diseño. Si un
> detalle del diseño es incoherente con el producto o con lo que el backend
> puede entregar, repórtalo igual y márcalo como **decisión de producto** en vez
> de callártelo o de inventar el dato.

---

## El agente del chrome compartido

El sidebar y el topbar se repiten en los 40 frames. Va un agente aparte que los
audite una sola vez contra **todas** las variantes. Interesa especialmente lo
que **cambia** entre ellas: `manager.pen` tiene el sidebar expandido (272, frame
`KgwzQ`) y colapsado (80, frame `FZjwU`). Si el front tiene una sola versión de
algo que el diseño varía por estado, eso es un hallazgo GRAVE.

## El agente de gráficas

Las gráficas no se auditan contra el `.pen` solo: se auditan contra el skill
`dataviz`. Ese agente corre el validador —no razona sobre él— y reporta:

```bash
node <skill dataviz>/scripts/validate_palette.js "<hex,hex,...>" --mode light
node <skill dataviz>/scripts/validate_palette.js "<hex,hex,...>" --mode dark
```

Cuando el diseño y el validador chocan, gana el validador. El hallazgo dice
ambos valores y por qué se cambió.

## Aplicar los hallazgos

En **secuencia**, una sola mano. Dos agentes editando el mismo `.tsx` se pisan.

Nunca aplicar una tanda con `sed` sobre todo el archivo: se come los comentarios
y deja el JSX corrupto de una forma que no salta a la vista. Bloque por bloque,
y `npx tsc --noEmit` al final.
