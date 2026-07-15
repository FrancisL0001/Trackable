// Route table with auth gating.
import { Navigate, Route, Routes } from "react-router-dom";
import { ErrorPage, errorKind } from "./components/ErrorPage";
import { Layout } from "./components/Layout";
import { CenterSpinner } from "./components/ui";
import { useAuth } from "./auth/AuthContext";
import { Login } from "./pages/Login";
import { Dashboard } from "./pages/Dashboard";
import { Calendar } from "./pages/Calendar";
import { Assignments } from "./pages/Assignments";
import { Tasks } from "./pages/Tasks";
import { Events } from "./pages/Events";
import { StudyTips } from "./pages/StudyTips";
import { Integrations } from "./pages/Integrations";
import { NotFound } from "./pages/NotFound";

export function App() {
  const { user, loading, bootError } = useAuth();

  if (loading) return <CenterSpinner label="Loading Trackable…" />;

  // Session restore failed because the server is down/erroring (not bad
  // credentials): show a server-down screen instead of bouncing to login.
  if (bootError) {
    return (
      <ErrorPage
        fullScreen
        kind={errorKind(bootError)}
        onRetry={() => window.location.reload()}
      />
    );
  }

  if (!user) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/calendar" element={<Calendar />} />
        <Route path="/assignments" element={<Assignments />} />
        <Route path="/tasks" element={<Tasks />} />
        <Route path="/events" element={<Events />} />
        <Route path="/study-tips" element={<StudyTips />} />
        <Route path="/integrations" element={<Integrations />} />
      </Route>
      <Route path="/login" element={<Navigate to="/" replace />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
