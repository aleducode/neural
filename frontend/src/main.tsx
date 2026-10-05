import { createRoot } from "react-dom/client";
import "./index.css";

import AppShell from "./islands/AppShell";
import Bookings from "./islands/Bookings";
import CalendarMonth from "./islands/CalendarMonth";
import ClassDetail from "./islands/ClassDetail";
import Classes from "./islands/Classes";
import Dashboard from "./islands/Dashboard";
import MemberDetail from "./islands/MemberDetail";
import Members from "./islands/Members";
import PackageDetail from "./islands/PackageDetail";
import Packages from "./islands/Packages";
import Payments from "./islands/Payments";
import Plans from "./islands/Plans";
import Videos from "./islands/Videos";
import Login from "./islands/Login";
import NotificationsTable from "./islands/NotificationsTable";
import SendNotification from "./islands/SendNotification";
import UsersTable from "./islands/UsersTable";

/**
 * Islas: Django sigue sirviendo la pagina, la sesion y los datos. React se
 * monta solo donde hace falta interaccion.
 *
 * Cada isla es un <div data-island="nombre"> con un
 * <script type="application/json" id="nombre-props"> al lado.
 */
const ISLANDS: Record<string, (props: any) => JSX.Element> = {
  "app-shell": AppShell,
  dashboard: Dashboard,
  members: Members,
  "member-detail": MemberDetail,
  "class-detail": ClassDetail,
  classes: Classes,
  bookings: Bookings,
  calendar: CalendarMonth,
  payments: Payments,
  plans: Plans,
  videos: Videos,
  packages: Packages,
  "package-detail": PackageDetail,
  login: Login,
  "notifications-table": NotificationsTable,
  "send-notification": SendNotification,
  "users-table": UsersTable,
};

/** El id del <script> de props: data-props si viene, si no "<isla>-props".
 *  Las pantallas de seccion comparten plantilla, asi que comparten id. */
function readProps(id: string): object {
  const node = document.getElementById(id);
  if (!node?.textContent) return {};
  try {
    return JSON.parse(node.textContent);
  } catch (error) {
    console.error(`[manager] props ilegibles en "${id}"`, error);
    return {};
  }
}

/**
 * El contenido nace oculto porque el shell lo adopta dentro del inset. Si el
 * shell no llega a montarse, hay que mostrarlo igual: un panel en blanco es
 * peor que uno sin estilos.
 */
function revealContent() {
  const content = document.getElementById("manager-content");
  if (content?.hidden) content.hidden = false;
}

document.querySelectorAll<HTMLElement>("[data-island]").forEach((node) => {
  const name = node.dataset.island;
  if (!name) return;
  const Island = ISLANDS[name];
  if (!Island) {
    console.warn(`[manager] no hay isla registrada con el nombre "${name}"`);
    return;
  }
  try {
    createRoot(node).render(<Island {...readProps(node.dataset.props ?? `${name}-props`)} />);
  } catch (error) {
    console.error(`[manager] la isla "${name}" no pudo montarse`, error);
  }
});

// Si el shell monto bien, para entonces ya adopto el contenido y esto no hace
// nada. Si algo fallo, al menos el panel se ve.
window.setTimeout(revealContent, 1500);
window.addEventListener("error", revealContent);
