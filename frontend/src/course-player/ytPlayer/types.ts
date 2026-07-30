export interface UseYouTubePlayerOptions {
  containerId: string;
  videoId: string;
  onReady?: () => void;
  onStateChange?: (state: number) => void;
}

export interface UseYouTubePlayerReturn {
  isReady: boolean;
  play: () => void;
  pause: () => void;
  loadVideo: (videoId: string) => void;

  getCurrentTime: () => number;
  getDuration: () => number;
  seekTo: (seconds: number) => void;
}
