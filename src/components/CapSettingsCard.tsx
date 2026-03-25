import React, { useEffect, useState } from "react";
import { Pencil, RotateCcw } from "lucide-react";

type PeriodMode = "daily" | "hourly" | "total";
type ActionMode = "exclude" | "return";

interface CapSettingsState {
  enabled: boolean;
  globalCap: string;
  period: PeriodMode;
  action: ActionMode;
  capReachedImmediately: boolean;
}

interface CapSettingsCardProps {
  className?: string;
  initialEnabled?: boolean;
  initialGlobalCap?: number | string;
  initialPeriod?: PeriodMode;
  initialAction?: ActionMode;
  // For DAILY/HOURLY modes
  todayClicks?: number;
  yesterdayClicks?: number;
  // For TOTAL mode
  totalClicks?: number;
  onChange?: (nextState: CapSettingsState) => void;
  onEdit?: (nextCap: number) => void;
  onResetTotal?: () => void;
}

const periodModes: Array<{ label: string; value: PeriodMode }> = [
  { label: "DAILY", value: "daily" },
  { label: "HOURLY", value: "hourly" },
  { label: "TOTAL", value: "total" },
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

export default function CapSettingsCard({
  className = "",
  initialEnabled = false,
  initialGlobalCap = "470",
  initialPeriod = "daily",
  initialAction = "exclude",
  todayClicks = 473,
  yesterdayClicks = 471,
  totalClicks = 800,
  onChange,
  onEdit,
  onResetTotal,
}: CapSettingsCardProps) {
  const [enabled, setEnabled] = useState(initialEnabled);
  const [globalCap, setGlobalCap] = useState(String(initialGlobalCap));
  const [savedCap, setSavedCap] = useState(String(initialGlobalCap));
  const [period, setPeriod] = useState<PeriodMode>(initialPeriod);
  const [action, setAction] = useState<ActionMode>(initialAction);
  const [capReachedImmediately, setCapReachedImmediately] = useState(false);
  const [warningMessage, setWarningMessage] = useState("");

  useEffect(() => {
    onChange?.({ enabled, globalCap, period, action, capReachedImmediately });
  }, [enabled, globalCap, period, action, capReachedImmediately, onChange]);

  const disabledUI = !enabled;

  const handleTotalReset = () => {
    onResetTotal?.();
    setWarningMessage("Total counter was reset.");
  };

  const tryApplyCapValue = (rawValue: string) => {
    const parsed = Number(rawValue);
    if (!Number.isFinite(parsed) || parsed <= 0) {
      setWarningMessage("Global Cap must be a positive number.");
      return;
    }

    if (period === "total" && parsed <= totalClicks) {
      const proceed = window.confirm(
        "You set cap below current spent clicks. Traffic will be stopped immediately. Continue?"
      );
      if (!proceed) {
        setGlobalCap(savedCap);
        return;
      }

      setCapReachedImmediately(true);
      setWarningMessage(
        "Cap reached immediately. New clicks are blocked by selected action."
      );
      const nextCap = String(parsed);
      setGlobalCap(nextCap);
      setSavedCap(nextCap);
      onEdit?.(parsed);
      return;
    }

    setCapReachedImmediately(false);
    setWarningMessage("");
    const nextCap = String(parsed);
    setGlobalCap(nextCap);
    setSavedCap(nextCap);
    onEdit?.(parsed);
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
          aria-label="Toggle Cap Settings"
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
        <span className="text-sm font-medium text-slate-600">Cap Settings</span>
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
            onBlur={() => {
              if (disabledUI) return;
              tryApplyCapValue(globalCap);
            }}
            onKeyDown={(event) => {
              if (event.key !== "Enter" || disabledUI) return;
              tryApplyCapValue(globalCap);
            }}
            disabled={disabledUI}
            className="h-11 w-full rounded border border-slate-300 bg-white px-3 pr-44 text-base text-slate-700 outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100 disabled:cursor-not-allowed"
          />

          <div className="absolute inset-y-0 right-16 flex items-center gap-2 text-sm font-semibold text-red-500">
            {period === "total" ? (
              <span>{totalClicks}</span>
            ) : (
              <>
                <span>{todayClicks}</span>
                <span>{yesterdayClicks}</span>
              </>
            )}
          </div>

          <div className="absolute inset-y-0 right-3 flex items-center gap-1">
            {period === "total" && (
              <button
                type="button"
                onClick={handleTotalReset}
                disabled={disabledUI}
                className="rounded p-1 text-slate-500 transition hover:bg-slate-200 hover:text-slate-700 disabled:cursor-not-allowed"
                aria-label="Reset total cap"
                title="Reset total cap"
              >
                <RotateCcw size={14} />
              </button>
            )}

            <button
              type="button"
              onClick={() => tryApplyCapValue(globalCap)}
              disabled={disabledUI}
              className="rounded p-1 text-slate-500 transition hover:bg-slate-200 hover:text-slate-700 disabled:cursor-not-allowed"
              aria-label="Edit global cap"
              title="Edit global cap"
            >
              <Pencil size={14} />
            </button>
          </div>
        </div>
        <p className="mt-2 min-h-4 text-xs text-red-600">{warningMessage}</p>

        <div className="mt-4 flex flex-wrap items-center gap-3">
          <div className="inline-flex overflow-hidden rounded border border-slate-200">
            {periodModes.map((mode) => (
              <button
                key={mode.value}
                type="button"
                disabled={disabledUI}
                onClick={() => {
                  setPeriod(mode.value);
                  setWarningMessage("");
                  setCapReachedImmediately(false);
                }}
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
