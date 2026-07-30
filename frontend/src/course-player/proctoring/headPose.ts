export interface ProctoringState {
  status: "idle" | "requesting" | "active" | "denied" | "error";
  isFaceDetected: boolean;
  isLookingAway: boolean;
  attentionLost: boolean;
  errorMessage?: string;
  stream: MediaStream | null;
}

export interface UseProctoringOptions {
  enabled: boolean;
  lookAwayThresholdMs?: number;
  onAttentionLost?: () => void;
  onAttentionRegained?: () => void;
}

// Head pose thresholds (pseudo-degrees based on ratio)
export const YAW_THRESHOLD = 25;
export const PITCH_THRESHOLD = 25;

// MediaPipe Face Mesh landmark indices
const NOSE_TIP = 1;
const LEFT_EYE_OUTER = 33;
const RIGHT_EYE_OUTER = 263;
const FOREHEAD = 10;
const CHIN = 152;

export function computeHeadPose(landmarks: { x: number; y: number; z: number }[]): {
  yaw: number;
  pitch: number;
} {
  const nose = landmarks[NOSE_TIP];
  const leftEye = landmarks[LEFT_EYE_OUTER];
  const rightEye = landmarks[RIGHT_EYE_OUTER];
  const top = landmarks[FOREHEAD];
  const bottom = landmarks[CHIN];

  // Yaw: horizontal ratio of nose between the two eyes
  const eyeDist = Math.sqrt(
    Math.pow(rightEye.x - leftEye.x, 2) + Math.pow(rightEye.y - leftEye.y, 2)
  );
  const eyeMidX = (leftEye.x + rightEye.x) / 2;
  const yawRatio = (nose.x - eyeMidX) / (eyeDist || 1);
  const yaw = yawRatio * 100; // approximate degrees

  // Pitch: vertical ratio of nose between forehead and chin
  const faceHeight = Math.sqrt(
    Math.pow(bottom.x - top.x, 2) + Math.pow(bottom.y - top.y, 2)
  );
  const faceMidY = (top.y + bottom.y) / 2;
  
  // Nose is typically below the center of the face (towards the chin)
  // We subtract ~0.15 to center the baseline pitch around 0 when looking straight
  const pitchRatio = (nose.y - faceMidY) / (faceHeight || 1);
  const pitch = (pitchRatio - 0.15) * 100; // approximate degrees

  return { yaw, pitch };
}
