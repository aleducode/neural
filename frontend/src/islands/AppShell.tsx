import { Bell, ChevronsUpDown, Dumbbell, LayoutDashboard, LogOut, Users } from "lucide-react";
import { useEffect, useRef } from "react";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Separator } from "@/components/ui/separator";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarRail,
  SidebarTrigger,
} from "@/components/ui/sidebar";

type Item = { label: string; url: string; icon: "dashboard" | "users" | "bell"; active: boolean };

type Props = {
  title: string;
  nav: { group: string; items: Item[] }[];
  user: { name: string; initials: string; role: string };
  logoutUrl: string;
  csrfToken: string;
};

const ICONS = { dashboard: LayoutDashboard, users: Users, bell: Bell };

export default function AppShell({ title, nav, user, logoutUrl, csrfToken }: Props) {
  const slot = useRef<HTMLDivElement>(null);

  // El contenido lo sigue renderizando Django. En vez de duplicarlo en React,
  // movemos ese nodo dentro del inset una sola vez, ya montado.
  useEffect(() => {
    const content = document.getElementById("manager-content");
    if (content && slot.current && content.parentElement !== slot.current) {
      slot.current.appendChild(content);
      content.hidden = false;
    }
  }, []);

  return (
    <SidebarProvider>
      <Sidebar variant="inset">
        <SidebarHeader>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton size="lg" asChild>
                <a href="/manager/">
                  <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                    <Dumbbell className="size-4" />
                  </div>
                  <div className="grid flex-1 text-left text-sm leading-tight">
                    <span className="truncate font-semibold">Neural</span>
                    <span className="truncate text-xs text-muted-foreground">Manager</span>
                  </div>
                </a>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarHeader>

        <SidebarContent>
          {nav.map((group) => (
            <SidebarGroup key={group.group}>
              <SidebarGroupLabel>{group.group}</SidebarGroupLabel>
              <SidebarMenu>
                {group.items.map((item) => {
                  const Icon = ICONS[item.icon];
                  return (
                    <SidebarMenuItem key={item.url}>
                      <SidebarMenuButton asChild isActive={item.active} tooltip={item.label}>
                        <a href={item.url}>
                          <Icon />
                          <span>{item.label}</span>
                        </a>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  );
                })}
              </SidebarMenu>
            </SidebarGroup>
          ))}
        </SidebarContent>

        <SidebarFooter>
          <SidebarMenu>
            <SidebarMenuItem>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <SidebarMenuButton
                    size="lg"
                    className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
                  >
                    <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-emerald-500 text-xs font-semibold text-white">
                      {user.initials}
                    </div>
                    <div className="grid flex-1 text-left text-sm leading-tight">
                      <span className="truncate font-semibold">{user.name}</span>
                      <span className="truncate text-xs text-muted-foreground">{user.role}</span>
                    </div>
                    <ChevronsUpDown className="ml-auto size-4" />
                  </SidebarMenuButton>
                </DropdownMenuTrigger>
                <DropdownMenuContent side="top" align="end" className="w-56">
                  {/* El logout va por POST: con GET bastaba un <img> ajeno
                      apuntando a esa URL para cerrarle la sesion a cualquiera. */}
                  <form method="post" action={logoutUrl}>
                    <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
                    <DropdownMenuItem asChild>
                      <button type="submit" className="w-full cursor-pointer">
                        <LogOut className="size-4" />
                        Cerrar sesión
                      </button>
                    </DropdownMenuItem>
                  </form>
                </DropdownMenuContent>
              </DropdownMenu>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarFooter>

        <SidebarRail />
      </Sidebar>

      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 border-b border-border px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <h2 className="text-sm font-medium text-foreground">{title}</h2>
        </header>
        <div ref={slot} className="flex-1 p-4 md:p-6" />
      </SidebarInset>
    </SidebarProvider>
  );
}
