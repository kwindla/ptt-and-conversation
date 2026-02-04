import "@pipecat-ai/voice-ui-kit/styles.css";
import "./App.css";

import {
  PipecatAppBase,
  Conversation,
  ConnectButton,
  VoiceVisualizer,
  ControlBar,
  Card,
  CardContent,
  usePipecatConnectionState,
} from "@pipecat-ai/voice-ui-kit";
import { ModeToggle } from "./components/ModeToggle";
import { PTTButton } from "./components/PTTButton";
import { MicButton } from "./components/MicButton";
import { KrispToggle } from "./components/KrispToggle";
import { useVoiceChatState } from "./hooks/useVoiceChatState";

interface VoiceChatContentProps {
  handleConnect?: () => void;
  handleDisconnect?: () => void;
}

function VoiceChatContent({
  handleConnect,
  handleDisconnect,
}: VoiceChatContentProps) {
  const { isConnected } = usePipecatConnectionState();
  const {
    mode,
    isPTTActive,
    krispEnabled,
    isMicMuted,
    handleModeChange,
    handlePTTStart,
    handlePTTStop,
    handleKrispToggle,
    handleMicToggle,
  } = useVoiceChatState();

  return (
    <div className="voice-chat-container">
      {/* Header */}
      <header className="voice-chat-header">
        <h1>Voice Chat</h1>
        <div className="header-controls">
          <div className="mode-indicator">
            Mode: <span className={mode}>{mode.toUpperCase()}</span>
          </div>
          {isConnected && (
            <KrispToggle
              enabled={krispEnabled}
              onToggle={handleKrispToggle}
            />
          )}
        </div>
      </header>

      {/* Main content area with conversation */}
      <main className="voice-chat-main">
        <Card className="conversation-card">
          <CardContent className="conversation-content">
            <Conversation
              assistantLabel="Assistant"
              clientLabel="You"
              noAutoscroll={false}
              noTextInput={true}
              textMode="llm"
            />
          </CardContent>
        </Card>
      </main>

      {/* Controls area */}
      <footer className="voice-chat-footer">
        <ControlBar className="control-bar">
          <div className="controls-left">
            <ConnectButton
              size="lg"
              onConnect={handleConnect}
              onDisconnect={handleDisconnect}
            />
          </div>

          {isConnected && (
            <>
              <div className="controls-center">
                <ModeToggle mode={mode} onModeChange={handleModeChange} />

                {mode === "ptt" ? (
                  <PTTButton
                    isActive={isPTTActive}
                    onStart={handlePTTStart}
                    onStop={handlePTTStop}
                    disabled={!isConnected}
                  />
                ) : (
                  <MicButton
                    isMuted={isMicMuted}
                    onToggle={handleMicToggle}
                    disabled={!isConnected}
                  />
                )}
              </div>

              <div className="controls-right">
                <VoiceVisualizer
                  participantType="local"
                  className="voice-viz"
                />
              </div>
            </>
          )}
        </ControlBar>

        <p className="mode-hint">
          {!isConnected
            ? "Click Connect to start"
            : mode === "ptt"
              ? "Hold the button to speak"
              : "Speak naturally - the bot will respond"}
        </p>
      </footer>

    </div>
  );
}

function App() {
  return (
    <PipecatAppBase
      transportType="smallwebrtc"
      connectParams={{
        connection_url: "http://localhost:7860/api/offer",
      }}
      clientOptions={{
        enableMic: false,  // Start with mic off (PTT mode)
        enableCam: false,
      }}
    >
      {({ client, handleConnect, handleDisconnect }) =>
        client ? (
          <VoiceChatContent
            handleConnect={handleConnect}
            handleDisconnect={handleDisconnect}
          />
        ) : null
      }
    </PipecatAppBase>
  );
}

export default App;
