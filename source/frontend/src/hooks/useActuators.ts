/**
 * useActuators.ts — Actuator state with optimistic updates.
 */
import { useCallback, useEffect, useState } from "react";
import { getActuators, setActuator } from "../api";

export function useActuators() {
  const [actuators, setActuators] = useState<Record<string, "ON" | "OFF">>({});
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const data = await getActuators();
      setActuators(data.actuators);
      setError(null);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 5000);
    return () => clearInterval(id);
  }, [refresh]);

  const toggle = useCallback(
    async (name: string) => {
      const next: "ON" | "OFF" = actuators[name] === "ON" ? "OFF" : "ON";
      // Optimistic update
      setActuators((prev) => ({ ...prev, [name]: next }));
      try {
        await setActuator(name, next);
      } catch {
        // Revert on error
        await refresh();
      }
    },
    [actuators, refresh],
  );

  return { actuators, loading, error, toggle, refresh };
}
