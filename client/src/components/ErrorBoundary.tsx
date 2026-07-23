// Last-resort boundary: a render crash shows a recoverable screen, not a blank page.
import { Component, type ReactNode } from "react";
import { ErrorPage } from "./ErrorPage";

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  render() {
    if (this.state.error) {
      return (
        <ErrorPage
          fullScreen
          kind="generic"
          detail={this.state.error.message}
          onRetry={() => window.location.reload()}
        />
      );
    }
    return this.props.children;
  }
}
