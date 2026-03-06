/**
 * components/sensors/StatusBadge.tsx — Small pill badge for sensor status.
 *
 * | status    | colour  | label   |
 * |-----------|---------|---------|
 * | "ok"      | emerald | OK      |
 * | "warning" | amber   | WARNING |
 * | null/""   | gray    | –       |
 */

interface StatusBadgeProps {
  status: "ok" | "warning" | string | null | undefined;
  /** Show a larger/smaller badge. Default: "sm". */
  size?: "xs" | "sm" | "md";
}

const COLOUR: Record<string, string> = {
  ok:      "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30",
  warning: "bg-amber-500/20   text-amber-400   border border-amber-500/30",
  default: "bg-gray-700/40    text-gray-500    border border-gray-700",
};

const SIZE_CLS: Record<string, string> = {
  xs: "text-[9px] px-1.5 py-0",
  sm: "text-[10px] px-2 py-0.5",
  md: "text-xs px-2.5 py-1",
};

export default function StatusBadge({
  status,
  size = "sm",
}: StatusBadgeProps) {
  const key    = status === "ok" || status === "warning" ? status : "default";
  const colour = COLOUR[key];
  const label  = status === "ok" ? "OK" : status === "warning" ? "WARNING" : "–";

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium uppercase tracking-wider ${colour} ${SIZE_CLS[size]}`}
    >
      {label}
    </span>
  );
}
