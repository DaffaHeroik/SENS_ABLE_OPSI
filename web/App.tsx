import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import DashboardLayout from "@/components/DashboardLayout";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";
import Instructions from "./pages/Instructions";
import Deploy from "./pages/Deploy";
import Reports from "./pages/Reports";
import GuestInstaller from "./pages/GuestInstaller";
import NotFound from "./pages/NotFound";
import { Route, Switch } from "wouter";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  return <DashboardLayout>{children}</DashboardLayout>;
}

function Router() {
  return (
    <Switch>
      <Route path="/owner">
        <ProtectedRoute><Home /></ProtectedRoute>
      </Route>
      <Route path="/" component={GuestInstaller} />
      <Route path="/install" component={GuestInstaller} />
      <Route path="/connection">
        <ProtectedRoute><Instructions /></ProtectedRoute>
      </Route>
      <Route path="/deploy">
        <ProtectedRoute><Deploy /></ProtectedRoute>
      </Route>
      <Route path="/reports">
        <ProtectedRoute><Reports /></ProtectedRoute>
      </Route>
      <Route path="/404" component={NotFound} />
      <Route component={NotFound} />
    </Switch>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="dark">
        <TooltipProvider>
          <Toaster theme="dark" />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}
