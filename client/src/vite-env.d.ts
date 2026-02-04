/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_LOCAL_WEBRTC_URL?: string;
  readonly VITE_PIPECAT_START_ENDPOINT?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
