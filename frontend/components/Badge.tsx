export default function Badge({ value }: { value: string }) {
  return (
    <span
      className={`pill ${value === "HOT" ? "hot" : value === "WARM" ? "warm" : "cold"}`}
    >
      {value}
    </span>
  );
}
