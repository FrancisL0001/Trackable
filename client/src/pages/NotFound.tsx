import { Link } from "react-router-dom";

export function NotFound() {
  return (
    <div className="grid place-items-center min-h-screen p-5 text-center">
      <div>
        <h1 className="text-5xl mb-2">404</h1>
        <p className="text-content-muted mb-6">This page wandered off.</p>
        <Link to="/" className="btn btn-primary">
          Back to dashboard
        </Link>
      </div>
    </div>
  );
}
