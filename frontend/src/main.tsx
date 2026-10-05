import { createRoot } from "react-dom/client";
import "./index.css";

import AppShell from "./islands/AppShell";
import Dashboard from "./islands/Dashboard";
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
  "notifications-table": NotificationsTable,
  "send-notification": SendNotification,
  "users-table": UsersTable,
};

function readProps(name: string): object {
  const node = document.getElementById(`${name}-props`);
  if (!node?.textContent) return {};
  try {
    return JSON.parse(node.textContent);
  } catch (error) {
    console.error(`[manager] props ilegibles para la isla "${name}"`, error);
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
    createRoot(node).render(<Island {...readProps(name)} />);
  } catch (error) {
    console.error(`[manager] la isla "${name}" no pudo montarse`, error);
  }
});

// Si el shell monto bien, para entonces ya adopto el contenido y esto no hace
// nada. Si algo fallo, al menos el panel se ve.
window.setTimeout(revealContent, 1500);
window.addEventListener("error", revealContent);
