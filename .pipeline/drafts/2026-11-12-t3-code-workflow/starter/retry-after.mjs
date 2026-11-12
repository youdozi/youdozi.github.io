export function retryAfterMs(header) {
  const seconds = Number.parseInt(header, 10);
  return Number.isFinite(seconds) ? seconds * 1000 : null;
}
