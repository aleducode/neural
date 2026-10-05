# La vara de front del manager

Lo que se revisa antes de decir que una pantalla está lista, más allá de que se
parezca al diseño. Ordenado por lo que más caro sale cuando falta.

---

## 1. Los datos son reales o no están

La regla que más plata ahorra. Ver §3 del SKILL. En corto:

- Cifra del `.pen` copiada tal cual = bug.
- Etiqueta que promete un dato que el backend no produce = bug grave.
- Widget sin dato detrás = no se implementa, se reporta.
- Si el dato existe pero es otro, se renombra la etiqueta para que diga la
  verdad. "Payment Method" sin medio de pago guardado es "Plan".

El manager hoy se alimenta de: `User`, `Profile`, `UserMembership`,
`NeuralPlan`, `UserPaymentReference`, `UserTraining`, `Slot`, `Classes`,
`TrainingType`, `UserStats`, `UserStrike`, `Device`, `PushNotification`. **No
hay modelo de entrenador** ni de medio de pago: cualquier widget que los pida va
al informe, no a la pantalla.

## 2. Estados

El diseño dibuja el camino feliz. Faltan casi siempre:

- **Vacío** — con una acción, no solo un dibujo triste.
- **Cargando** — honesto: si no hay denominador, no pintes una barra al 0% con
  un total inventado. Decí qué está haciendo.
- **Error** — con el motivo y qué puede hacer la persona.
- **Parcial** — se cargaron 8 de 10; qué pasó con las otras 2.
- **Sin permiso** — distinto de error. El manager es `SuperStaffRequiredMixin`.

## 3. Accesibilidad

- `:focus-visible` con anillo en **todo** control, incluidos los `<a>`
  disfrazados de botón y los `<div>` con `tabindex`.
- Una tabla hecha con `div` necesita `role="table"/"row"/"cell"`. Usá `<table>`.
- `aria-current="page"` en el item activo del sidebar.
- Un control deshabilitado explica **por qué** en su `title`.
- Contraste: el texto secundario del diseño (`#666d80` sobre `#ffffff`) da
  5,2:1 y pasa; el terciario (`#818898`) da 3,4:1 y **no** pasa AA para 12px.
  Usalo solo en texto de 14px o más, o reportalo.

## 4. Controles muertos

Si el diseño dibuja un menú `…`, un buscador o un filtro "Monthly" y no hay nada
detrás, **no se implementa**. La persona lo clickea, no pasa nada, y deja de
confiar en el resto de la pantalla. Se reporta como decisión de producto.

## 5. Gráficas

Manda el skill `dataviz`, no el `.pen`. Ver §6 del SKILL. Lo que más se rompe:

- Dos series de escala distinta metidas en un doble eje. Son dos gráficas.
- Un color de serie usado también como color de texto.
- Una leyenda que falta con 2 series, o una leyenda de más con 1.
- Un ramp secuencial que no es monótono en luminosidad.
- El validador no corrido.

## 6. Responsive

- El lienzo del diseño es 1440 con sidebar de 272: el contenido es 1168.
  Contenedor fluido, no anchos fijos en las dos columnas de una fila.
- Definí qué colapsa, qué se apila y qué scrollea.
- Una tabla de anchos fijos necesita `overflow-x` y bases más chicas en el
  breakpoint, **en todas sus columnas**. La que te olvides rompe la fila.
- Probar a ~400px antes de dar nada por terminado.

## 7. Higiene de las islas

- Props por `{{ props|json_script:"..." }}`, nunca `|safe`.
- Toda isla pasa por el registro de `main.tsx` y por su `revealContent()`: si
  falla el montaje, la página muestra el HTML de Django, no un blanco.
- Nombres de entry del bundle fijos: si cambiás uno, cambiá el template.
- Nada de `any`. `npx tsc --noEmit` limpio antes de dar nada por terminado.
- Comentarios: los del repo están en español. Seguí el archivo que estás
  tocando, no tu preferencia.

## 8. Antes de decir que está listo

```bash
npx tsc --noEmit
npx vite build
```

En el navegador, con valores computados y no a ojo:

```js
getComputedStyle(el).padding
document.querySelector('[data-sidebar]').getBoundingClientRect().width   // ¿272?
[...document.querySelectorAll('svg')].map(s => s.getBoundingClientRect().width)
```

Más la pantalla a 400px y una pasada con el teclado, sin mouse.

**Y no se despliega sin permiso explícito.**
