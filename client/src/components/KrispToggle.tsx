interface KrispToggleProps {
  enabled: boolean;
  onToggle: () => void;
  disabled?: boolean;
}

export function KrispToggle({ enabled, onToggle, disabled }: KrispToggleProps) {
  return (
    <button
      className={`krisp-toggle ${enabled ? "enabled" : "disabled"}`}
      onClick={onToggle}
      disabled={disabled}
      title={enabled ? "Krisp noise reduction enabled" : "Krisp noise reduction disabled"}
    >
      <span className="krisp-icon">
        {enabled ? (
          // Noise reduction on icon
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
            <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
            <line x1="12" y1="19" x2="12" y2="23" />
            <line x1="8" y1="23" x2="16" y2="23" />
          </svg>
        ) : (
          // Noise reduction off icon (mic with slash)
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="1" y1="1" x2="23" y2="23" />
            <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6" />
            <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2c0 .97-.23 1.88-.64 2.69" />
            <line x1="12" y1="19" x2="12" y2="23" />
            <line x1="8" y1="23" x2="16" y2="23" />
          </svg>
        )}
      </span>
      <span className="krisp-label">Krisp {enabled ? "On" : "Off"}</span>
    </button>
  );
}
