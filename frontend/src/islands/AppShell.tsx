import {
  Bell,
  CalendarCheck,
  CalendarDays,
  ChevronsUpDown,
  Dumbbell,
  Layers,
  LayoutDashboard,
  Library,
  LogOut,
  Users,
  Video,
  Wallet,
} from "lucide-react";
import { useEffect, useRef } from "react";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Separator } from "@/components/ui/separator";
import { ThemeToggle } from "@/components/ui/theme-toggle";
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

type Item = { label: string; url: string; icon: keyof typeof ICONS; active: boolean };

type Props = {
  title: string;
  nav: { group: string; items: Item[] }[];
  user: { name: string; initials: string; role: string };
  logoutUrl: string;
  csrfToken: string;
  logoUrl: string;
};

const ICONS = {
  dashboard: LayoutDashboard,
  users: Users,
  bell: Bell,
  dumbbell: Dumbbell,
  "calendar-check": CalendarCheck,
  calendar: CalendarDays,
  wallet: Wallet,
  layers: Layers,
  video: Video,
  library: Library,
};

export default function AppShell({ title, nav, user, logoutUrl, csrfToken, logoUrl }: Props) {
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
      <Sidebar className="border-r border-sidebar-border">
        <SidebarHeader className="h-20 flex-row items-center justify-between px-6 py-5 group-data-[collapsible=icon]:px-4">
          <a href="/manager/" className="flex items-center gap-2.5 no-underline">
            <span className="flex size-7 flex-none items-center justify-center overflow-hidden rounded-full bg-primary shadow-icon-box">
              <img src={logoUrl} alt="" className="size-4 object-contain" />
            </span>
            <span className="truncate text-base font-semibold text-sidebar-foreground group-data-[collapsible=icon]:hidden">
              Neural
            </span>
          </a>
        </SidebarHeader>

        <SidebarContent className="gap-4 px-4 py-2">
          {nav.map((group) => (
            <SidebarGroup key={group.group} className="gap-0.5 p-0">
              <SidebarGroupLabel className="h-auto px-3 pb-1 pt-0 text-xs font-medium text-faint">
                {group.group}
              </SidebarGroupLabel>
              <SidebarMenu>
                {group.items.map((item) => {
                  const Icon = ICONS[item.icon];
                  return (
                    <SidebarMenuItem key={item.url}>
                      <SidebarMenuButton
                        asChild
                        isActive={item.active}
                        tooltip={item.label}
                        aria-current={item.active ? "page" : undefined}
                        className="h-9 gap-2.5 rounded-md px-3 text-sm font-medium text-muted-foreground data-[active=true]:bg-sidebar-primary data-[active=true]:text-sidebar-primary-foreground [&>svg]:size-[18px]"
                      >
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
              <ThemeToggle />
            </SidebarMenuItem>
            <SidebarMenuItem>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <SidebarMenuButton
                    size="lg"
                    className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
                  >
                    <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-primary text-xs font-semibold text-primary-foreground">
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
        <header className="flex h-20 shrink-0 items-center gap-2 border-b border-border px-6">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <h2 className="text-base font-medium text-foreground">{title}</h2>
        </header>
        <div ref={slot} className="min-w-0 flex-1 p-4 md:p-6" />
      </SidebarInset>
    </SidebarProvider>
  );
}
