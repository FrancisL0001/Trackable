import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  ApiError,
  api,
  getToken,
  setToken,
  setUnauthorizedHandler,
} from "./client";

function mockFetch(status: number, body: unknown) {
  return vi.fn().mockResolvedValue({
    status,
    ok: status >= 200 && status < 300,
    text: async () => (body === undefined ? "" : JSON.stringify(body)),
  } as Response);
}

describe("api client", () => {
  beforeEach(() => {
    localStorage.clear();
    setUnauthorizedHandler(null);
  });

  it("stores and clears the token", () => {
    setToken("abc");
    expect(getToken()).toBe("abc");
    setToken(null);
    expect(getToken()).toBeNull();
  });

  it("attaches the auth token to requests", async () => {
    setToken("tok123");
    const fetchMock = mockFetch(200, { ok: true });
    vi.stubGlobal("fetch", fetchMock);

    await api.get("/api/items");

    const headers = fetchMock.mock.calls[0][1].headers;
    expect(headers.Authorization).toBe("Bearer tok123");
  });

  it("throws ApiError with the server detail on failure", async () => {
    vi.stubGlobal("fetch", mockFetch(409, { detail: "Email exists" }));
    await expect(api.post("/api/auth/register", {}, true)).rejects.toThrow(ApiError);
    await expect(api.post("/api/auth/register", {}, true)).rejects.toThrow(
      "Email exists"
    );
  });

  it("invokes the unauthorized handler on 401", async () => {
    const onUnauth = vi.fn();
    setUnauthorizedHandler(onUnauth);
    setToken("expired");
    vi.stubGlobal("fetch", mockFetch(401, { detail: "nope" }));

    await expect(api.get("/api/items")).rejects.toThrow(ApiError);
    expect(onUnauth).toHaveBeenCalledOnce();
  });

  it("returns undefined for 204 responses", async () => {
    setToken("t");
    vi.stubGlobal("fetch", mockFetch(204, undefined));
    const result = await api.del("/api/items/1");
    expect(result).toBeUndefined();
  });
});
