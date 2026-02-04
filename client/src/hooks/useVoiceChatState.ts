import { useCallback, useState, useEffect } from "react";
import { usePipecatClient } from "@pipecat-ai/client-react";
import { usePipecatConnectionState } from "@pipecat-ai/voice-ui-kit";
import { RTVIEvent } from "@pipecat-ai/client-js";

export type Mode = "ptt" | "live";

export function useVoiceChatState() {
  const client = usePipecatClient();
  const { isConnected } = usePipecatConnectionState();
  const [mode, setMode] = useState<Mode>("ptt");
  const [isPTTActive, setIsPTTActive] = useState(false);
  const [krispEnabled, setKrispEnabled] = useState(true);
  const [isMicMuted, setIsMicMuted] = useState(true);  // Starts muted in PTT mode

  // Listen for server responses
  useEffect(() => {
    if (!client) return;

    const handleResponse = (response: unknown) => {
      console.log("Server response:", response);
    };

    client.on(RTVIEvent.MessageResponse, handleResponse);

    return () => {
      client.off(RTVIEvent.MessageResponse, handleResponse);
    };
  }, [client]);

  const handleModeChange = useCallback(
    async (newMode: Mode) => {
      if (!client || !isConnected || newMode === mode) return;

      try {
        console.log(`Switching to ${newMode} mode`);
        client.sendClientMessage("ptt-mode-change", { mode: newMode });
        setMode(newMode);

        // Reset PTT state when switching modes
        setIsPTTActive(false);

        // Enable mic if switching to live mode, disable if switching to PTT
        if (newMode === "live") {
          await client.enableMic(true);
          setIsMicMuted(false);
        } else {
          await client.enableMic(false);
          setIsMicMuted(true);
        }
      } catch (error) {
        console.error("Failed to change mode:", error);
      }
    },
    [client, isConnected, mode]
  );

  const handlePTTStart = useCallback(async () => {
    if (!client || !isConnected || mode !== "ptt") return;

    try {
      console.log("PTT: Starting");
      setIsPTTActive(true);
      await client.enableMic(true);
      client.sendClientMessage("ptt-state", { speaking: true });
    } catch (error) {
      console.error("Failed to start PTT:", error);
      setIsPTTActive(false);
    }
  }, [client, isConnected, mode]);

  const handlePTTStop = useCallback(async () => {
    if (!client || !isConnected || mode !== "ptt") return;

    try {
      console.log("PTT: Stopping");
      client.sendClientMessage("ptt-state", { speaking: false });
      await client.enableMic(false);
      setIsPTTActive(false);
    } catch (error) {
      console.error("Failed to stop PTT:", error);
    }
  }, [client, isConnected, mode]);

  const handleKrispToggle = useCallback(() => {
    if (!client || !isConnected) return;

    const newState = !krispEnabled;
    console.log(`Krisp: ${newState ? "enabling" : "disabling"}`);
    client.sendClientMessage("krisp-control", { enable: newState });
    setKrispEnabled(newState);
  }, [client, isConnected, krispEnabled]);

  const handleMicToggle = useCallback(async () => {
    if (!client || !isConnected || mode !== "live") return;

    try {
      const newMuted = !isMicMuted;
      await client.enableMic(!newMuted);
      setIsMicMuted(newMuted);
      console.log(`Mic: ${newMuted ? "muted" : "unmuted"}`);
    } catch (error) {
      console.error("Failed to toggle mic:", error);
    }
  }, [client, isConnected, mode, isMicMuted]);

  return {
    mode,
    isPTTActive,
    krispEnabled,
    isMicMuted,
    handleModeChange,
    handlePTTStart,
    handlePTTStop,
    handleKrispToggle,
    handleMicToggle,
  };
}
