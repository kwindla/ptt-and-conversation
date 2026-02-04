type Mode = "ptt" | "live";

interface ModeToggleProps {
  mode: Mode;
  onModeChange: (mode: Mode) => void;
}

export function ModeToggle({ mode, onModeChange }: ModeToggleProps) {
  return (
    <div className="mode-toggle">
      <button
        className={mode === "ptt" ? "active" : ""}
        onClick={() => onModeChange("ptt")}
      >
        Push to Talk
      </button>
      <button
        className={mode === "live" ? "active" : ""}
        onClick={() => onModeChange("live")}
      >
        Live
      </button>
    </div>
  );
}
