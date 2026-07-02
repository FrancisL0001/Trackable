import { Link } from "react-router-dom";
import { Icon } from "../components/Icon";

export function NotFound() {
  return (
    <div className="grid place-items-center min-h-screen p-5 text-center bg-[radial-gradient(800px_400px_at_50%_-10%,var(--primary-soft),transparent)]">
      <div>
        <span className="inline-grid place-items-center w-16 h-16 rounded-full bg-primary-soft text-primary-strong mb-4">
          <Icon name="search" size={28} />
        </span>
        <h1 className="text-5xl mb-2 m-0">404</h1>
        <p className="text-content-muted mb-7 mt-2">This page wandered off.</p>
        <Link to="/" className="btn btn-primary">
          <Icon name="chevron-left" size={16} /> Back to dashboard
        </Link>
      </div>
    </div>
  );
}
