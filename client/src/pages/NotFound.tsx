import { Link } from "react-router-dom";
import { ErrorPage } from "../components/ErrorPage";

export function NotFound() {
  return (
    <ErrorPage
      fullScreen
      kind="notfound"
      action={
        <Link to="/" className="btn btn-primary">
          Back to dashboard
        </Link>
      }
    />
  );
}
