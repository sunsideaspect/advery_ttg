import React, { useEffect, useState } from "react";
import { Pencil, RotateCcw } from "lucide-react";

type PeriodMode = "daily" | "hourly" | "lifetime";
type ActionMode = "exclude" | "return";

interface FrequencyCapState {
  enabled: boolean;
  globalCap: string;
  period: PeriodMode;
  action: ActionMode;
}

interface FrequencyCapCardProps {
  className?: string;
  initialEnabled?: boolean;
  initialGlobalCap?: number | string;
  initialPeriod?: PeriodMode;
  initialAction?: ActionMode;
  counters?: [number, number];
  onChange?: (nextState: FrequencyCapState) => void;
  onEdit?: () => void;
  onResetLifetime?: () => void;
}

const periodModes: Array<{ label: string; value: PeriodMode }> = [
  { label: "DAILY", value: "daily" },
  { label: "HOURLY", value: "hourly" },
  { label: "LIFETIME", value: "lifetime" },
];

const actionModes: Array<{ label: string; value: ActionMode }> = [
  { label: "EXCLUDE", value: "exclude" },
  { label: "RETURN", value: "return" },
];

const baseButtonClasses =
  "h-8 px-4 text-[11px] font-semibold uppercase tracking-wide transition-colors";

function segmentedButtonClasses(active: boolean) {
  return `${baseButtonClasses} ${
    active
      ? "bg-blue-100 text-blue-700"
      : "bg-slate-100 text-slate-400 hover:bg-slate-200"
  }`;
}

export default function FrequencyCapCard({
  className = "",
  initialEnabled = false,
  initialGlobalCap = "470",
  initialPeriod = "daily",
  initialAction = "exclude",
  counters = [473, 471],
  onChange,
  onEdit,
  onResetLifetime,
}: FrequencyCapCardProps) {
  const [enabled, setEnabled] = useState(initialEnabled);
  const [globalCap, setGlobalCap] = useState(String(initialGlobalCap));
  const [period, setPeriod] = useState<PeriodMode>(initialPeriod);
  const [action, setAction] = useState<ActionMode>(initialAction);

  useEffect(() => {
    onChange?.({ enabled, globalCap, period, action });
  }, [enabled, globalCap, period, action, onChange]);

  const disabledUI = !enabled;

  const handleLifetimeReset = () => {
    onResetLifetime?.();
    setGlobalCap("");
  };

  return (
    <div
      className={`w-full rounded-md border border-slate-200 bg-slate-100 p-6 shadow-sm ${className}`}
    >
      <div className="mb-5 flex items-center gap-3">
        <button
          type="button"
          role="switch"
          aria-checked={enabled}
          aria-label="Toggle Frequency Cap"
          onClick={() => setEnabled((prev) => !prev)}
          className={`relative inline-flex h-6 w-11 items-center rounded-full border transition-colors ${
            enabled
              ? "border-blue-300 bg-blue-500"
              : "border-slate-300 bg-slate-200"
          }`}
        >
          <span
            className={`inline-block h-5 w-5 transform rounded-full bg-white shadow transition-transform ${
              enabled ? "translate-x-5" : "translate-x-0.5"
            }`}
          />
        </button>
        <span className="text-sm font-medium text-slate-600">Frequency Cap</span>
      </div>

      <div className={disabledUI ? "opacity-60" : ""}>
        <label
          htmlFor="global-cap-input"
          className="mb-1 block text-[11px] font-semibold uppercase tracking-wide text-slate-500"
        >
          Global Cap
        </label>

        <div className="relative">
          <input
            id="global-cap-input"
            type="number"
            value={globalCap}
            onChange={(event) => setGlobalCap(event.target.value)}
            disabled={disabledUI}
            className="h-11 w-full rounded border border-slate-300 bg-white px-3 pr-44 text-base text-slate-700 outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100 disabled:cursor-not-allowed"
          />

          <div className="absolute inset-y-0 right-16 flex items-center gap-2 text-sm font-semibold text-red-500">
            <span>{counters[0]}</span>
            <span>{counters[1]}</span>
          </div>

          <div className="absolute inset-y-0 right-3 flex items-center gap-1">
            {period === "lifetime" && (
              <button
                type="button"
                onClick={handleLifetimeReset}
                disabled={disabledUI}
                className="rounded p-1 text-slate-500 transition hover:bg-slate-200 hover:text-slate-700 disabled:cursor-not-allowed"
                aria-label="Reset lifetime cap"
                title="Reset lifetime cap"
              >
                <RotateCcw size={14} />
              </button>
            )}

            <button
              type="button"
              onClick={onEdit}
              disabled={disabledUI}
              className="rounded p-1 text-slate-500 transition hover:bg-slate-200 hover:text-slate-700 disabled:cursor-not-allowed"
              aria-label="Edit global cap"
              title="Edit global cap"
            >
              <Pencil size={14} />
            </button>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-3">
          <div className="inline-flex overflow-hidden rounded border border-slate-200">
            {periodModes.map((mode) => (
              <button
                key={mode.value}
                type="button"
                disabled={disabledUI}
                onClick={() => setPeriod(mode.value)}
                className={segmentedButtonClasses(period === mode.value)}
              >
                {mode.label}
              </button>
            ))}
          </div>

          <div className="inline-flex overflow-hidden rounded border border-slate-200">
            {actionModes.map((mode) => (
              <button
                key={mode.value}
                type="button"
                disabled={disabledUI}
                onClick={() => setAction(mode.value)}
                className={segmentedButtonClasses(action === mode.value)}
              >
                {mode.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
