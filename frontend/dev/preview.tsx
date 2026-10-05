import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";

import "../src/index.css";
import AppShell from "../src/islands/AppShell";
import Dashboard from "../src/islands/Dashboard";
import Login from "../src/islands/Login";
import NotificationsTable from "../src/islands/NotificationsTable";
import SendNotification from "../src/islands/SendNotification";
import UsersTable from "../src/islands/UsersTable";
import Bookings from "../src/islands/Bookings";
import ClassDetail from "../src/islands/ClassDetail";
import MemberDetail from "../src/islands/MemberDetail";
import CalendarMonth from "../src/islands/CalendarMonth";
import Classes from "../src/islands/Classes";
import Members from "../src/islands/Members";
import Payments from "../src/islands/Payments";
import Plans from "../src/islands/Plans";
import * as data from "./props";
import { secciones } from "./sections";

const URLS = {
  userDetailUrl: "/manager/users/0/",
  sendUrl: "/enviar",
  calendarUrl: "/calendario",
  classDetailUrl: "/clase/0/",
  backUrl: "/clases",
  csrfToken: "dev",
};

/** El feed de notificaciones pide datos al servidor; aqui lo simulamos. */
const FEED = "/mock/notifications";
const DETALLE = "/mock/notification/0/";
const originalFetch = window.fetch.bind(window);
window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
  // La isla pasa un objeto URL absoluto, no un string relativo: se compara el
  // pathname o el mock no entra y vuelve el index.html de Vite.
  const crudo = String(typeof input === "string" ? input : (input as Request).url ?? input);
  const url = new URL(crudo, location.origin).pathname + new URL(crudo, location.origin).search;
  const detalle = url.match(/\/mock\/notification\/(\d+)\//);
  if (detalle) {
    return new Response(JSON.stringify(data.notificationDetail(Number(detalle[1]))), {
      headers: { "Content-Type": "application/json" },
    });
  }
  if (!url.startsWith(FEED)) return originalFetch(input as any, init);
  const page = Number(new URL(url, location.origin).searchParams.get("page") ?? 1);
  return new Response(JSON.stringify(data.notificationsPage(page)), {
    headers: { "Content-Type": "application/json" },
  });
};

/**
 * Preview local de las islas, sin Django ni base de datos.
 * El shell adopta #manager-content, asi que aqui lo simulamos igual.
 */
const TITULOS: Record<string, string> = {
  dashboard: "Dashboard",
  usuarios: "Usuarios",
  "usuario detalle": "Detalle del usuario",
  "clase detalle": "Detalle de la clase",
  clases: "Clases",
  reservas: "Reservas",
  calendario: "Calendario",
  pagos: "Pagos",
  planes: "Planes",
  usuarios: "Usuarios",
  notificaciones: "Notificaciones",
  enviar: "Enviar notificación",
};

const PANTALLAS = {
  dashboard: () => <Dashboard {...(secciones.dashboard as any)} {...URLS} />,
  usuarios: () => <Members {...(secciones.members as any)} {...URLS} />,
  "usuario detalle": () => (
    <MemberDetail {...(secciones.memberDetail as any)} {...URLS} backUrl="/usuarios" />
  ),
  "clase detalle": () => (
    <ClassDetail {...(secciones.classDetail as any)} {...URLS} backUrl="/clases" />
  ),
  clases: () => <Classes {...(secciones.classes as any)} {...URLS} />,
  reservas: () => <Bookings {...(secciones.bookings as any)} {...URLS} />,
  calendario: () => <CalendarMonth {...(secciones.calendar as any)} {...URLS} />,
  pagos: () => <Payments {...(secciones.payments as any)} {...URLS} />,
  planes: () => <Plans {...(secciones.plans as any)} {...URLS} />,
  usuarios: () => <UsersTable {...(data.usersTable as any)} />,
  notificaciones: () => (
    <NotificationsTable
      kpis={data.notificationsKpis as any}
      feedUrl={FEED}
      detailUrl={DETALLE}
      sendUrl="/enviar"
      userDetailUrl="/manager/users/0/"
      types={[
        { value: "general", label: "General" },
        { value: "training_reminder", label: "Recordatorio de entrenamiento" },
        { value: "membership_expiring", label: "Membresía por vencer" },
      ]}
      statuses={[
        { value: "sent", label: "Enviada" },
        { value: "read", label: "Leída" },
        { value: "failed", label: "Fallida" },
      ]}
    />
  ),
  enviar: () => (
    <SendNotification
      users={data.usersTable.users.map((u) => ({
        id: u.id, name: u.name, initials: u.initials, email: u.email,
      }))}
      types={[
        { value: "general", label: "General" },
        { value: "promotion", label: "Promoción" },
      ]}
      lockedUser={null}
      defaultType="general"
      cancelUrl="#"
      csrfToken="dev"
    />
  ),
  login: () => <Login {...data.login} />,
  "login con error": () => <Login {...data.loginError} />,
};

type Pantalla = keyof typeof PANTALLAS;

const RUTAS: Record<string, Pantalla> = {
  "/dashboard": "dashboard",
  "/usuarios": "usuarios",
  "/usuario-detalle": "usuario detalle",
  "/clase-detalle": "clase detalle",
  "/clases": "clases",
  "/reservas": "reservas",
  "/calendario": "calendario",
  "/pagos": "pagos",
  "/planes": "planes",
  "/usuarios": "usuarios",
  "/notificaciones": "notificaciones",
  "/enviar": "enviar",
  "/login": "login",
  "/login-error": "login con error",
};

function pantallaDeLaRuta(): Pantalla {
  return RUTAS[window.location.pathname] ?? "dashboard";
}

function rutaDe(pantalla: Pantalla) {
  return Object.keys(RUTAS).find((r) => RUTAS[r] === pantalla) ?? "/dashboard";
}

function Preview() {
  const [pantalla, setPantalla] = useState<Pantalla>(pantallaDeLaRuta);

  // Rutas de verdad, sin #. Interceptamos los enlaces internos para que el
  // sidebar navegue como lo hara en produccion contra Django.
  useEffect(() => {
    const onPop = () => setPantalla(pantallaDeLaRuta());
    window.addEventListener("popstate", onPop);

    const onClick = (event: MouseEvent) => {
      const link = (event.target as HTMLElement)?.closest?.("a");
      const href = link?.getAttribute("href");
      if (!href || !(href in RUTAS)) return;
      event.preventDefault();
      window.history.pushState({}, "", href);
      setPantalla(RUTAS[href]);
    };
    document.addEventListener("click", onClick);

    return () => {
      window.removeEventListener("popstate", onPop);
      document.removeEventListener("click", onClick);
    };
  }, []);
  const esLogin = pantalla.startsWith("login");

  const selector = (
    <div className="fixed bottom-4 left-1/2 z-50 flex max-w-[95vw] -translate-x-1/2 gap-1 overflow-x-auto rounded-full border border-border bg-background p-1 shadow-lg">
      {(Object.keys(PANTALLAS) as Pantalla[]).map((key) => (
        <button
          key={key}
          onClick={() => { window.history.pushState({}, "", rutaDe(key)); setPantalla(key); }}
          className={`whitespace-nowrap rounded-full px-3 py-1.5 text-xs font-medium capitalize ${
            pantalla === key ? "bg-primary text-primary-foreground" : "text-muted-foreground"
          }`}
        >
          {key}
        </button>
      ))}
    </div>
  );

  if (esLogin) {
    return (
      <>
        {PANTALLAS[pantalla]()}
        {selector}
      </>
    );
  }

  return (
    <>
      <AppShell
        {...(data.shell as any)}
        title={TITULOS[pantalla] ?? pantalla}
        nav={data.shell.nav.map((g) => ({
          ...g,
          items: g.items.map((i) => ({ ...i, active: RUTAS[i.url] === pantalla })),
        }))}
      />
      {/* Lo que en produccion renderiza Django */}
      <div id="manager-content" hidden>
        {PANTALLAS[pantalla]()}
      </div>
      {selector}
    </>
  );
}

createRoot(document.getElementById("preview")!).render(<Preview />);
