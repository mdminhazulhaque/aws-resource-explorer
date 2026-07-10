export function serviceOf(arn) {
  return arn.split(":")[2] ?? "";
}

export function facetCounts(arns) {
  const counts = new Map();
  for (const arn of arns) {
    const service = serviceOf(arn);
    counts.set(service, (counts.get(service) ?? 0) + 1);
  }
  return [...counts.entries()].sort((a, b) => a[0].localeCompare(b[0]));
}

export function applyFilters(arns, text, activeServices) {
  const query = text.trim().toLowerCase();
  return arns.filter((arn) =>
    (!query || arn.toLowerCase().includes(query)) &&
    (activeServices.size === 0 || activeServices.has(serviceOf(arn)))
  );
}
