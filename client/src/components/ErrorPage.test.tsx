import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { ApiError } from "../api/client";
import { QueryError, errorKind } from "./ErrorPage";

describe("errorKind", () => {
  it("classifies network, server, and not-found errors", () => {
    expect(errorKind(new ApiError(0, "Cannot reach the server."))).toBe("offline");
    expect(errorKind(new ApiError(500, "boom"))).toBe("server");
    expect(errorKind(new ApiError(502, "bad gateway"))).toBe("server");
    expect(errorKind(new ApiError(404, "missing"))).toBe("notfound");
    expect(errorKind(new ApiError(422, "invalid"))).toBe("generic");
    expect(errorKind(new Error("render crash"))).toBe("generic");
  });
});

describe("QueryError", () => {
  it("shows the server-down page for unreachable backends and retries", () => {
    const onRetry = vi.fn();
    render(
      <MemoryRouter>
        <QueryError error={new ApiError(0, "Cannot reach the server.")} onRetry={onRetry} />
      </MemoryRouter>
    );
    expect(screen.getByText("Can't reach the server")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /try again/i }));
    expect(onRetry).toHaveBeenCalledOnce();
  });

  it("shows the server-error page for 5xx responses", () => {
    render(
      <MemoryRouter>
        <QueryError error={new ApiError(500, "internal")} />
      </MemoryRouter>
    );
    expect(screen.getByText("Something broke on our end")).toBeInTheDocument();
  });

  it("offers a way home on not-found", () => {
    render(
      <MemoryRouter>
        <QueryError error={new ApiError(404, "missing")} />
      </MemoryRouter>
    );
    expect(screen.getByText("Page not found")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /back to dashboard/i })).toHaveAttribute(
      "href",
      "/"
    );
  });
});
