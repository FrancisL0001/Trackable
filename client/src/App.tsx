// Route table with auth gating.
import { Navigate, Route, Routes } from "react-router-dom";
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
  const { user, loading } = useAuth();

  if (loading) return <CenterSpinner label="Loading Trackable…" />;

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
