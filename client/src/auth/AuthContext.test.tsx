import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AuthProvider, useAuth } from "./AuthContext";
import { getToken } from "../api/client";
import { authApi } from "../api/endpoints";

vi.mock("../api/endpoints", () => ({
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    me: vi.fn(),
  },
}));

function Harness() {
  const { user, loading, login, logout } = useAuth();
  if (loading) return <div>loading</div>;
  return (
    <div>
      <span data-testid="user">{user ? user.email : "anonymous"}</span>
      <button onClick={() => login("a@b.edu", "password123")}>login</button>
      <button onClick={logout}>logout</button>
    </div>
  );
}

describe("AuthContext", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it("starts anonymous when there is no token", async () => {
    render(
      <AuthProvider>
        <Harness />
      </AuthProvider>
    );
    await waitFor(() =>
      expect(screen.getByTestId("user")).toHaveTextContent("anonymous")
    );
  });

  it("logs in, stores the token, then logs out", async () => {
    vi.mocked(authApi.login).mockResolvedValue({
      access_token: "tok",
      token_type: "bearer",
      user: {
        id: 1,
        email: "a@b.edu",
        full_name: "A",
        timezone: "UTC",
        reminder_soon_days: 7,
        created_at: "2026-01-01T00:00:00Z",
      },
    });

    render(
      <AuthProvider>
        <Harness />
      </AuthProvider>
    );
    await waitFor(() => expect(screen.getByTestId("user")).toBeInTheDocument());

    await userEvent.click(screen.getByText("login"));
    await waitFor(() =>
      expect(screen.getByTestId("user")).toHaveTextContent("a@b.edu")
    );
    expect(getToken()).toBe("tok");

    await userEvent.click(screen.getByText("logout"));
    await waitFor(() =>
      expect(screen.getByTestId("user")).toHaveTextContent("anonymous")
    );
    expect(getToken()).toBeNull();
  });

  it("restores a session from a stored token", async () => {
    localStorage.setItem("trackable_token", "stored");
    vi.mocked(authApi.me).mockResolvedValue({
      id: 2,
      email: "restored@b.edu",
      full_name: "R",
      timezone: "UTC",
      reminder_soon_days: 7,
      created_at: "2026-01-01T00:00:00Z",
    });

    render(
      <AuthProvider>
        <Harness />
      </AuthProvider>
    );
    await waitFor(() =>
      expect(screen.getByTestId("user")).toHaveTextContent("restored@b.edu")
    );
  });
});
