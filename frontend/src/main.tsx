import { createRoot } from "react-dom/client";
import "./index.css";

import UsersTable from "./islands/UsersTable";

/**
 * Islas: Django sigue sirviendo la pagina, la sesion y los datos. React se
 * monta solo donde hace falta interaccion.
 *
 * Cada isla es un <div data-island="nombre"> con un
 * <script type="application/json" id="nombre-props"> al lado.
 */
const ISLANDS: Record<string, (props: any) => JSX.Element> = {
  "users-table": UsersTable,
};

function readProps(name: string): unknown {
  const node = document.getElementById(`${name}-props`);
  if (!node?.textContent) return {};
  try {
    return JSON.parse(node.textContent);
  } catch (error) {
    console.error(`[manager] props ilegibles para la isla "${name}"`, error);
    return {};
  }
}

document.querySelectorAll<HTMLElement>("[data-island]").forEach((node) => {
  const name = node.dataset.island;
  if (!name) return;
  const Island = ISLANDS[name];
  if (!Island) {
    console.warn(`[manager] no hay isla registrada con el nombre "${name}"`);
    return;
  }
  createRoot(node).render(<Island {...(readProps(name) as object)} />);
});
