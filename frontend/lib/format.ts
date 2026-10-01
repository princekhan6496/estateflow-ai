export function formatINR(value: number) {
  return `₹${(value / 100000).toFixed(1).replace(/\.0$/, '')}L`
}
