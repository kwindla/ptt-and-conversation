import { useRef, useEffect } from "react";

interface PTTButtonProps {
  isActive: boolean;
  onStart: () => void;
  onStop: () => void;
  disabled?: boolean;
}

export function PTTButton({
  isActive,
  onStart,
  onStop,
  disabled,
}: PTTButtonProps) {
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Handle window blur to stop PTT if window loses focus
  useEffect(() => {
    const handleWindowBlur = () => {
      if (isActive) {
        onStop();
      }
    };

    window.addEventListener("blur", handleWindowBlur);
    return () => window.removeEventListener("blur", handleWindowBlur);
  }, [isActive, onStop]);

  const handlePointerDown = (e: React.PointerEvent) => {
    e.preventDefault();
    if (disabled) return;

    // Capture pointer to receive events even if pointer leaves the element
    buttonRef.current?.setPointerCapture(e.pointerId);
    onStart();
  };

  const handlePointerUp = (e: React.PointerEvent) => {
    e.preventDefault();
    if (disabled || !isActive) return;

    buttonRef.current?.releasePointerCapture(e.pointerId);
    onStop();
  };

  const handlePointerCancel = (e: React.PointerEvent) => {
    e.preventDefault();
    if (isActive) {
      onStop();
    }
  };

  const handleLostPointerCapture = () => {
    // Pointer capture was lost (e.g., touch interrupted by system gesture)
    if (isActive) {
      onStop();
    }
  };

  return (
    <button
      ref={buttonRef}
      className={`ptt-btn ${isActive ? "active" : ""}`}
      onPointerDown={handlePointerDown}
      onPointerUp={handlePointerUp}
      onPointerCancel={handlePointerCancel}
      onLostPointerCapture={handleLostPointerCapture}
      onContextMenu={(e) => e.preventDefault()}
      disabled={disabled}
    >
      {isActive ? "Speaking..." : "Hold to Talk"}
    </button>
  );
}
