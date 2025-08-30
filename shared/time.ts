const start = Date.now();

export function nowDay(): number {
  const msInDay = 1000 * 60 * 60 * 24;
  return (Date.now() - start) / msInDay;
}
