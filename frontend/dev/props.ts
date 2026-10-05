/** Datos de muestra para ver las islas sin levantar Django.
    Los numeros salen de produccion para que el preview no mienta. */

export const LOGO = "/brain.png";

export const shell = {
  title: "Dashboard",
  // Mismo arbol que SuperStaffRequiredMixin.NAV en neural/manager/views.py.
  nav: [
    { group: "Principal", items: [{ label: "Dashboard", url: "/dashboard", icon: "dashboard", active: true }] },
    { group: "Gestión", items: [
      { label: "Usuarios", url: "/usuarios", icon: "users", active: false },
      { label: "Clases", url: "/clases", icon: "dumbbell", active: false },
      { label: "Reservas", url: "/reservas", icon: "calendar-check", active: false },
    ] },
    { group: "Operación", items: [
      { label: "Calendario", url: "/calendario", icon: "calendar", active: false },
    ] },
    { group: "Finanzas", items: [
      { label: "Pagos", url: "/pagos", icon: "wallet", active: false },
      { label: "Planes", url: "/planes", icon: "layers", active: false },
    ] },
    { group: "Comunicación", items: [
      { label: "Notificaciones", url: "/notificaciones", icon: "bell", active: false },
    ] },
  ],
  user: { name: "Alejandro Duque", initials: "AD", role: "Superusuario" },
  logoutUrl: "#",
  csrfToken: "dev",
  logoUrl: LOGO,
};

export const dashboard = {
  today: "domingo, 5 de octubre de 2026",
  // Los KPI arrancan de cifras reales de produccion (~740 usuarios, ~98 que
  // entrenan por semana) para que el preview no dibuje un gimnasio que no es.
  kpis: [
    { key: "usuarios", icon: "users", label: "Total usuarios", value: "742", delta: 1.8, basis: "frente al cierre del mes pasado" },
    { key: "ingresos", icon: "wallet", label: "Ingresos del mes", value: "$ 4.320.000", delta: 12.4, basis: "frente a los primeros 5 días del mes pasado" },
    { key: "membresias", icon: "badge-check", label: "Membresías activas", value: "130", delta: -3.7, basis: "frente al cierre del mes pasado" },
    { key: "checkins", icon: "scan-line", label: "Check-ins de hoy", value: "41", delta: 7.9, basis: "frente al mismo día de la semana pasada" },
  ],
  growth: {
    points: [
      { label: "Nov", nuevos: 18, activos: 71 },
      { label: "Dic", nuevos: 11, activos: 58 },
      { label: "Ene", nuevos: 46, activos: 88 },
      { label: "Feb", nuevos: 29, activos: 92 },
      { label: "Mar", nuevos: 24, activos: 95 },
      { label: "Abr", nuevos: 21, activos: 90 },
      { label: "May", nuevos: 26, activos: 97 },
      { label: "Jun", nuevos: 19, activos: 93 },
      { label: "Jul", nuevos: 23, activos: 87 },
      { label: "Ago", nuevos: 31, activos: 94 },
      { label: "Sep", nuevos: 27, activos: 98 },
      { label: "Oct", nuevos: 6, activos: 41 },
    ],
    total: 281,
    delta: -66.7,
    range: "de noviembre a octubre",
    series: [
      { key: "nuevos" as const, label: "Usuarios nuevos" },
      { key: "activos" as const, label: "Usuarios que entrenaron" },
    ],
  },
  classes: [
    { id: 1, name: "Funcional training", kind: "Clase grupal", duration: "60 min", bookings: 486, image: "/classes/cardio.jpg" },
    { id: 2, name: "Movilidad", kind: "Clase grupal", duration: "45 min", bookings: 173, image: "/classes/movilidad.jpg" },
    { id: 3, name: "Personalizado", kind: "Entrenamiento individual", duration: null, bookings: 54, image: "/classes/fuerza.jpg" },
  ],
  revenue: {
    segments: [
      { id: 1, label: "Mensualidad", value: 28800000, share: 62.1, amount: "$ 28.800.000" },
      { id: 2, label: "Trimestre", value: 12150000, share: 26.2, amount: "$ 12.150.000" },
      { id: 3, label: "Semestre", value: 5400000, share: 11.7, amount: "$ 5.400.000" },
    ],
    total: "$ 46.350.000",
    period: "últimos 12 meses",
  },
  payments: [
    { id: 1, userId: 12, reference: "A7F2K9QX3M1P", name: "Ana María Muñoz", initials: "AM", plan: "Mensualidad", amount: "$ 120.000", date: "4 Oct 2026", paid: true, status: "Pagado" },
    { id: 2, userId: 48, reference: "B3L8R2WZ7N4T", name: "Camilo Silva", initials: "CS", plan: "Trimestre", amount: "$ 324.000", date: "3 Oct 2026", paid: true, status: "Pagado" },
    { id: 3, userId: 91, reference: "C9M4V6YH2K8D", name: "Beatriz Zuluaga", initials: "BZ", plan: "Mensualidad", amount: "$ 120.000", date: "3 Oct 2026", paid: false, status: "Pendiente" },
    { id: 4, userId: 23, reference: "D5N1X7TJ9Q3F", name: "Mauricio Rendón", initials: "MR", plan: "Semestre", amount: "$ 600.000", date: "2 Oct 2026", paid: true, status: "Pagado" },
    { id: 5, userId: 67, reference: "E2P6Z4GB8L5S", name: "Nora Elena Cardona", initials: "NC", plan: "Mensualidad", amount: "$ 120.000", date: "1 Oct 2026", paid: true, status: "Pagado" },
    { id: 6, userId: 15, reference: "F8Q3C5KD1W7R", name: "Clara Múnera", initials: "CM", plan: "Trimestre", amount: "$ 324.000", date: "30 Sep 2026", paid: true, status: "Pagado" },
  ],
  gaps: [] as string[],
  usersUrl: "/usuarios",
  userDetailUrl: "/manager/users/0/",
  sendUrl: "/enviar",
};

export const usersTable = {
  users: Array.from({ length: 48 }, (_, i) => ({
    id: i + 1,
    name: ["Ana María Muñoz", "Camilo Silva", "Beatriz Zuluaga", "Sin nombre"][i % 4],
    initials: ["AM", "CS", "BZ", "CU"][i % 4],
    email: `usuario${i + 1}@gmail.com`,
    phone: "+57 300 000 0000",
    joined: "12 Sep 2026",
    devices: i % 3,
    membership: i % 3 === 0 ? null : { expires: "30 Nov 2026" },
  })),
  detailUrl: "/manager/users/0/",
};

export const login = { csrfToken: "dev", errors: [] as string[], email: "", logoUrl: LOGO };
export const loginError = { csrfToken: "dev", errors: ["Credenciales inválidas."], email: "admin@neural.com.co", logoUrl: LOGO };

/** Qué filas fallaron, para que el modal cuente lo mismo que la tabla. */
const fallidas = new Set<number>();

export function notificationsPage(page: number) {
  const titulos = [
    ["Membresía por vencer", "Tu membresía vence en 3 días. ¡Renuévala pronto!", "membership_expiring", "sent", "Enviada"],
    ["Recordatorio de entrenamiento", "Tu clase de Funcional empieza a las 09:00.", "training_reminder", "sent", "Enviada"],
    ["💪 Nueva reacción", "Camilo reaccionó a tu publicación", "general", "read", "Leída"],
    ["📢 Nueva publicación", "Ana María compartió un entrenamiento", "general", "failed", "Fallida"],
  ];
  const usuarios = [
    ["Ana María Muñoz", "AM"], ["Camilo Silva", "CS"],
    ["Beatriz Zuluaga", "BZ"], ["Mauricio Rendón", "MR"],
  ];
  return {
    results: Array.from({ length: 30 }, (_, i) => {
      const t = titulos[(i + page) % titulos.length];
      const s = usuarios[(i + page) % usuarios.length];
      const id = page * 100 + i;
      if (t[3] === "failed") fallidas.add(id);
      return {
        id,
        userId: (i % 4) + 1,
        userName: s[0],
        userInitials: s[1],
        userPhoto: i % 4 === 0 ? "/classes/movilidad.jpg" : null,
        attempts: t[3] === "failed" ? 2 : 1,
        failures: t[3] === "failed" ? 2 : 0,
        title: t[0],
        body: t[1],
        type: t[2] === "general" ? "General" : t[2] === "sent" ? "Enviada" : "Recordatorio",
        status: t[3],
        statusLabel: t[4],
        created: "04 Oct 2026, 09:1" + (i % 10),
      };
    }),
    page,
    pages: 236,
    total: 7063,
  };
}


/** El detalle que pide el modal. Las dos formas que importan: el envío que
    funcionó y el que falló con el error real de Expo. */
export function notificationDetail(id: number) {
  const fallo = fallidas.has(id);
  const base = {
    id,
    userId: 1,
    userName: "Mauricio Rendón",
    userInitials: "MR",
    userPhoto: null,
    userEmail: "mauricio.rendon35@gmail.com",
    title: fallo ? "📢 Nueva publicación" : "Membresía por vencer",
    body: fallo
      ? "Ana María compartió un entrenamiento"
      : "Tu membresía vence en 3 días. ¡Renuévala pronto!",
    type: "General",
    status: fallo ? "failed" : "delivered",
    statusLabel: fallo ? "Fallida" : "Entregada",
    created: "4 Oct 2026, 09:14",
    sentAt: fallo ? null : "4 Oct 2026, 09:14",
    readAt: null,
    scheduledFor: null,
    data: { notification_id: id, screen: "community" },
  };

  const request = {
    to: "ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]",
    title: base.title,
    body: base.body,
    sound: "default",
    data: base.data,
  };

  if (!fallo) {
    return {
      ...base,
      attempts: 1,
      failures: 0,
      summary: null,
      logs: [
        {
          id: 1,
          device: "iOS",
          deviceId: "A1B2C3D4E5F6G7H8",
          deviceActive: true,
          token: "…xxxxxxxxxxxx",
          ok: true,
          status: "Éxito",
          error: null,
          receipt: "8b1d2f4a-1c3e-4a7b-9f2d-6e5c4b3a2d1f",
          at: "4 Oct 2026, 09:14",
          request,
          response: { data: [{ status: "ok", id: "8b1d2f4a-1c3e-4a7b-9f2d-6e5c4b3a2d1f" }] },
        },
      ],
    };
  }

  return {
    ...base,
    attempts: 2,
    failures: 2,
    summary: "\u00ab...\u00bb is not a registered push notification recipient",
    logs: [
      {
        id: 1,
        device: "Android",
        deviceId: "Z9Y8X7W6V5U4T3S2",
        deviceActive: false,
        token: "…yyyyyyyyyyyy",
        ok: false,
        status: "Error",
        error: "\u00abExponentPushToken[yyyy]\u00bb is not a registered push notification recipient",
        receipt: null,
        at: "4 Oct 2026, 09:14",
        request,
        response: {
          data: [
            {
              status: "error",
              message: "\u00abExponentPushToken[yyyy]\u00bb is not a registered push notification recipient",
              details: { error: "DeviceNotRegistered" },
            },
          ],
        },
      },
      {
        id: 2,
        device: "iOS",
        deviceId: "Q1W2E3R4T5Y6U7I8",
        deviceActive: true,
        token: "…zzzzzzzzzzzz",
        ok: false,
        status: "Error",
        error: "Connection aborted: timed out after 10s",
        receipt: null,
        at: "4 Oct 2026, 09:14",
        request,
        response: null,
      },
    ],
  };
}

export const notificationsKpis = [
  { key: "hoy", icon: "bell", label: "Enviadas hoy", value: "148", delta: 6.4, basis: "frente a ayer" },
  { key: "entregadas", icon: "badge-check", label: "Entregadas (30 días)", value: "3.914", delta: null, basis: "" },
  { key: "fallidas", icon: "circle-x", label: "Fallidas (30 días)", value: "212", delta: null, basis: "" },
  { key: "tasa", icon: "percent", label: "Tasa de entrega", value: "95%", delta: null, basis: "" },
];
