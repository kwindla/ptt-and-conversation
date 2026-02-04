interface MicButtonProps {
  isMuted: boolean;
  onToggle: () => void;
  disabled?: boolean;
}

export function MicButton({ isMuted, onToggle, disabled }: MicButtonProps) {
  return (
    <button
      className={`mic-btn ${isMuted ? "muted" : "unmuted"}`}
      onClick={onToggle}
      disabled={disabled}
    >
      <span className="mic-icon">{isMuted ? "🔇" : "🎤"}</span>
      <span>{isMuted ? "Muted" : "Unmuted"}</span>
    </button>
  );
}
