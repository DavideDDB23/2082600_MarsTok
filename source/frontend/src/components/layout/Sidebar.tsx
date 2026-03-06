/**
 * components/layout/Sidebar.tsx — Fixed left-side navigation.
 *
 * Receives `connected` (SSE live-link status) so it can render a small
 * status indicator dot next to the brand logo.
 */
import { NavLink } from "react-router-dom";
import {
  Activity,
  Bell,
  Gauge,
  LayoutDashboard,
  Lock,
  Power,
  Settings2,
  Zap,
} from "lucide-react";

const NAV = [
  { to: "/",            label: "Dashboard",         icon: LayoutDashboard },
  { to: "/environment", label: "Environment",        icon: Activity        },
  { to: "/power",       label: "Power",              icon: Zap             },
  { to: "/airlock",     label: "Airlock & Thermal",  icon: Lock            },
  { to: "/actuators",   label: "Actuators",          icon: Power           },
  { to: "/rules",       label: "Rules",              icon: Settings2       },
  { to: "/alerts",      label: "Alerts",             icon: Bell            },
];

interface SidebarProps {
  /** Whether the SSE connection to /api/stream is active. */
  connected?: boolean;
}

export default function Sidebar({ connected = false }: SidebarProps) {
  return (
    <aside className="w-56 shrink-0 bg-gray-900 border-r border-gray-800 flex flex-col">
      {/* ── Brand ───────────────────────────────────────────────────────── */}
      <div className="flex items-center gap-2 px-5 py-5 border-b border-gray-800">
        <Gauge size={20} className="text-mars-500" />
        <span className="font-bold text-white text-sm tracking-wide">MARS OPS</span>
        {/* Connection indicator dot */}
        <span
          title={connected ? "Live data connected" : "Connecting…"}
          className={`ml-auto h-2 w-2 rounded-full shrink-0 ${
            connected ? "bg-emerald-400 animate-pulse" : "bg-gray-600"
          }`}
        />
      </div>

      {/* ── Navigation ──────────────────────────────────────────────────── */}
      <nav className="flex-1 overflow-y-auto py-3 space-y-0.5 px-2">
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? "bg-mars-500/20 text-mars-400 font-medium"
                  : "text-gray-400 hover:bg-gray-800 hover:text-gray-100"
              }`
            }
          >
            <Icon size={15} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* ── Footer ──────────────────────────────────────────────────────── */}
      <div className="px-5 py-3 border-t border-gray-800">
        <p className="text-[10px] text-gray-600">Laboratory of Advanced Programming</p>
      </div>
    </aside>
  );
}
