// Client-side defensive URL guard. React does not sanitize anchor hrefs, so we
// only render links for http(s) URLs and treat anything else as plain text.

const SAFE_SCHEMES = new Set(["http:", "https:"]);

export function safeHref(url: string | null | undefined): string | undefined {
  if (!url) return undefined;
  try {
    const parsed = new URL(url, window.location.origin);
    return SAFE_SCHEMES.has(parsed.protocol) && parsed.host ? url : undefined;
  } catch {
    return undefined;
  }
}
