"use client";
import Link from "next/link";
import { Home, Users, Building2, Plus, ChevronRight } from "lucide-react";
export default function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex">
      <aside className="hidden md:flex w-60 border-r border-[#e7e7e2] bg-white p-5 flex-col">
        <div className="text-lg font-bold tracking-tight mb-10">
          EstateFlow<span className="text-[#285943]"> AI</span>
        </div>
        <nav className="space-y-1 text-sm">
          <Link
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-[#f5f5f2]"
            href="/"
          >
            <Home size={16} />
            Dashboard
          </Link>
          <Link
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-[#f5f5f2]"
            href="/leads"
          >
            <Users size={16} />
            Leads
          </Link>
          <Link
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-[#f5f5f2]"
            href="/properties"
          >
            <Building2 size={16} />
            Properties
          </Link>
        </nav>
        <div className="mt-auto text-xs text-neutral-400">
          Focused sales workspace
          <br />
          v1.0
        </div>
      </aside>
      <main className="flex-1 min-w-0">{children}</main>
    </div>
  );
}
