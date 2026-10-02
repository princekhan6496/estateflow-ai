import Link from "next/link";
import { formatINR } from "../lib/format";
export default function PropertyCard({
  row,
  compact = false,
}: {
  row: any;
  compact?: boolean;
}) {
  const p = row.property || row;
  return (
    <Link
      href={`/properties/${p.id}`}
      className="surface rounded-xl p-4 block hover:border-neutral-400 transition"
    >
      <div className="flex justify-between gap-3">
        <div>
          <div className="font-semibold text-sm">{p.project_name}</div>
          <div className="text-xs muted mt-1">
            {p.property_code} · {p.location}
          </div>
        </div>
        {row.match_score != null && (
          <div className="text-sm font-bold">{row.match_score}%</div>
        )}
      </div>
      <div className="flex gap-5 mt-4 text-xs">
        <span>{p.bhk} BHK</span>
        <span>{formatINR(p.price)}</span>
        <span>{p.carpet_area} sq ft</span>
        <span>{p.parking_available ? "Parking" : ""}</span>
      </div>
      {!compact && row.match_reasons && (
        <div className="mt-3 text-xs space-y-1">
          {row.match_reasons.slice(0, 3).map((x: string) => (
            <div key={x} className="text-[#285943]">
              ✓ {x}
            </div>
          ))}
          {row.mismatch_reasons?.slice(0, 1).map((x: string) => (
            <div key={x} className="text-[#856716]">
              △ {x}
            </div>
          ))}
        </div>
      )}
    </Link>
  );
}
