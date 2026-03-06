/**
 * ActuatorCard.tsx — Displays one actuator with an ON/OFF toggle button.
 */
import { Power } from "lucide-react";

interface Props {
  name:     string;
  state:    "ON" | "OFF";
  onToggle: (name: string) => void;
}

export function ActuatorCard({ name, state, onToggle }: Props) {
  const isOn = state === "ON";

  return (
    <div className={`card flex items-center justify-between transition-colors ${
      isOn ? "border-green-700" : "border-gray-800"
    }`}>
      <div className="flex items-center gap-3">
        <Power
          size={20}
          className={isOn ? "text-green-400" : "text-gray-600"}
        />
        <div>
          <p className="text-sm font-medium text-gray-100">{name}</p>
          <p className={`text-xs font-semibold ${isOn ? "text-green-400" : "text-gray-500"}`}>
            {state}
          </p>
        </div>
      </div>

      <button
        onClick={() => onToggle(name)}
        className={`btn text-xs ${isOn ? "btn-danger" : "btn-primary"}`}
      >
        Turn {isOn ? "OFF" : "ON"}
      </button>
    </div>
  );
}
