import { useAuth } from "@/_core/hooks/useAuth";
import { startLogin } from "@/const";
import { Button } from "@/components/ui/button";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Activity, Cable, Cpu, FileChartColumn, LogOut, PanelLeft, ShieldCheck } from "lucide-react";
import { useLocation } from "wouter";

const menuItems = [
  { icon: Activity, label: "Gateway", path: "/owner" },
  { icon: Cpu, label: "Deploy", path: "/deploy" },
  { icon: Cable, label: "Connection", path: "/connection" },
  { icon: FileChartColumn, label: "Reports", path: "/reports" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { loading, user, logout } = useAuth();
  const [location, setLocation] = useLocation();

  if (loading) {
    return <div className="min-h-screen blueprint-grid" aria-label="Loading secure gateway" />;
  }

  if (!user) {
    return (
      <div className="min-h-screen blueprint-grid flex items-center justify-center p-6">
        <section className="cad-frame max-w-md p-8 text-center">
          <div className="mx-auto mb-6 grid h-14 w-14 place-items-center border border-cyan-300/60 bg-cyan-300/10">
            <ShieldCheck className="h-7 w-7 text-cyan-200" />
          </div>
          <p className="blueprint-label">Owner console</p>
          <h1 className="mt-3 text-3xl font-bold tracking-tight text-white">SENS-Able Gateway</h1>
          <p className="mt-4 leading-7 text-slate-300">This dashboard is restricted to the project owner. The public ingestion endpoint remains token-protected for ESP32 devices.</p>
          <Button onClick={startLogin} className="mt-7 w-full bg-cyan-300 text-blue-950 hover:bg-cyan-200">Sign in to dashboard</Button>
        </section>
      </div>
    );
  }

  return (
    <SidebarProvider>
      <Sidebar collapsible="icon" className="border-r border-cyan-100/15 bg-[#051a45]/95 text-slate-100">
        <SidebarHeader className="h-20 border-b border-cyan-100/15 px-3">
          <div className="flex h-full items-center gap-3">
            <PanelLeft className="h-5 w-5 text-cyan-200" />
            <div className="min-w-0 group-data-[collapsible=icon]:hidden">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-200">SENS-Able</p>
              <p className="truncate text-sm font-semibold text-white">ESP32 Gateway</p>
            </div>
          </div>
        </SidebarHeader>
        <SidebarContent className="pt-4">
          <SidebarMenu className="px-2">
            {menuItems.map(item => {
              const active = location === item.path;
              return (
                <SidebarMenuItem key={item.path}>
                  <SidebarMenuButton
                    isActive={active}
                    tooltip={item.label}
                    onClick={() => setLocation(item.path)}
                    className="h-11 text-slate-200 hover:bg-cyan-200/10 hover:text-white data-[active=true]:bg-cyan-300/15 data-[active=true]:text-cyan-100"
                  >
                    <item.icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              );
            })}
          </SidebarMenu>
        </SidebarContent>
        <SidebarFooter className="border-t border-cyan-100/15 p-3">
          <p className="mb-3 truncate px-2 text-xs text-slate-400 group-data-[collapsible=icon]:hidden">{user.email || user.name || "Owner"}</p>
          <Button variant="ghost" onClick={logout} className="w-full justify-start text-slate-300 hover:bg-red-400/10 hover:text-red-200">
            <LogOut className="mr-2 h-4 w-4" />
            <span className="group-data-[collapsible=icon]:hidden">Sign out</span>
          </Button>
        </SidebarFooter>
      </Sidebar>
      <SidebarInset className="blueprint-grid min-h-screen bg-[#061a44]">
        <header className="flex h-16 items-center gap-3 border-b border-cyan-100/15 bg-[#061a44]/85 px-4 backdrop-blur-md lg:px-8">
          <SidebarTrigger className="text-cyan-100 hover:bg-cyan-200/10" />
          <span className="blueprint-label hidden sm:inline">Secure sensor test environment</span>
          <div className="ml-auto flex items-center gap-2 text-xs font-medium text-emerald-200">
            <span className="h-2 w-2 rounded-full bg-emerald-300 shadow-[0_0_14px_2px_rgba(110,231,183,0.5)]" />
            HTTPS gateway ready
          </div>
        </header>
        <main className="flex-1 p-4 lg:p-8">{children}</main>
      </SidebarInset>
    </SidebarProvider>
  );
}
