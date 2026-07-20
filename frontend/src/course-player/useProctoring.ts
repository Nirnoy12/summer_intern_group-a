import { useEffect, useRef, useState, useCallback } from "react";
import { FaceLandmarker, FilesetResolver } from "@mediapipe/tasks-vision";
import type { FaceLandmarkerResult } from "@mediapipe/tasks-vision";

export interface ProctoringState {
  status: "idle" | "requesting" | "active" | "denied" | "error";
  isFaceDetected: boolean;
  isLookingAway: boolean;
  attentionLost: boolean;
  errorMessage?: string;
  stream: MediaStream | null;
}

interface UseProctoringOptions {
  enabled: boolean;
  lookAwayThresholdMs?: number;
  onAttentionLost?: () => void;
  onAttentionRegained?: () => void;
}

// Head pose thresholds (pseudo-degrees based on ratio)
const YAW_THRESHOLD = 25;
const PITCH_THRESHOLD = 25;

// MediaPipe Face Mesh landmark indices
const NOSE_TIP = 1;
const LEFT_EYE_OUTER = 33;
const RIGHT_EYE_OUTER = 263;
const FOREHEAD = 10;
const CHIN = 152;

function computeHeadPose(landmarks: { x: number; y: number; z: number }[]): {
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

export function useProctoring({
  enabled,
  lookAwayThresholdMs = 3000,
  onAttentionLost,
  onAttentionRegained,
}: UseProctoringOptions): ProctoringState {
  const [state, setState] = useState<ProctoringState>({
    status: "idle",
    isFaceDetected: false,
    isLookingAway: false,
    attentionLost: false,
    stream: null,
  });

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const faceLandmarkerRef = useRef<FaceLandmarker | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const rafRef = useRef<number>(0);
  const lookAwayStartRef = useRef<number | null>(null);
  const attentionLostRef = useRef(false);
  const onAttentionLostRef = useRef(onAttentionLost);
  const onAttentionRegainedRef = useRef(onAttentionRegained);
  const lastDetectionTimeRef = useRef<number>(0);

  // Keep callback refs fresh
  onAttentionLostRef.current = onAttentionLost;
  onAttentionRegainedRef.current = onAttentionRegained;

  const cleanup = useCallback(() => {
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = 0;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
      videoRef.current.remove();
      videoRef.current = null;
    }
    if (faceLandmarkerRef.current) {
      faceLandmarkerRef.current.close();
      faceLandmarkerRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (!enabled) {
      cleanup();
      setState({
        status: "idle",
        isFaceDetected: false,
        isLookingAway: false,
        attentionLost: false,
        stream: null,
      });
      return;
    }

    let cancelled = false;

    async function init() {
      setState((s) => ({ ...s, status: "requesting" }));

      // 1. Request webcam
      let stream: MediaStream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 320, height: 240, facingMode: "user" },
        });
      } catch (err) {
        if (!cancelled) {
          const isDenied =
            err instanceof DOMException &&
            (err.name === "NotAllowedError" || err.name === "PermissionDeniedError");
          setState({
            status: isDenied ? "denied" : "error",
            isFaceDetected: false,
            isLookingAway: false,
            attentionLost: false,
            errorMessage: isDenied
              ? "Camera permission denied"
              : "Failed to access camera",
            stream: null,
          });
        }
        return;
      }

      if (cancelled) {
        stream.getTracks().forEach((t) => t.stop());
        return;
      }

      streamRef.current = stream;

      // 2. Create hidden video element
      const video = document.createElement("video");
      video.setAttribute("autoplay", "");
      video.setAttribute("playsinline", "");
      video.setAttribute("muted", "");
      video.muted = true;
      video.style.position = "absolute";
      video.style.width = "1px";
      video.style.height = "1px";
      video.style.opacity = "0";
      video.style.pointerEvents = "none";
      video.style.overflow = "hidden";
      document.body.appendChild(video);
      video.srcObject = stream;
      videoRef.current = video;

      await video.play();

      if (cancelled) {
        cleanup();
        return;
      }

      // 3. Initialize FaceLandmarker
      try {
        const vision = await FilesetResolver.forVisionTasks(
          "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
        );
        if (cancelled) return;

        const faceLandmarker = await FaceLandmarker.createFromOptions(vision, {
          baseOptions: {
            modelAssetPath:
              "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
            delegate: "GPU",
          },
          runningMode: "VIDEO",
          numFaces: 1,
          outputFaceBlendshapes: false,
          outputFacialTransformationMatrixes: false,
        });

        if (cancelled) {
          faceLandmarker.close();
          return;
        }

        faceLandmarkerRef.current = faceLandmarker;
        setState((s) => ({ ...s, status: "active", stream: streamRef.current }));

        // 4. Start detection loop
        function detectLoop() {
          if (cancelled) return;

          const now = performance.now();
          // Throttle to ~15fps to keep CPU low
          if (now - lastDetectionTimeRef.current < 66) {
            rafRef.current = requestAnimationFrame(detectLoop);
            return;
          }
          lastDetectionTimeRef.current = now;

          const vid = videoRef.current;
          const fl = faceLandmarkerRef.current;

          if (!vid || !fl || vid.readyState < 2) {
            rafRef.current = requestAnimationFrame(detectLoop);
            return;
          }

          let result: FaceLandmarkerResult;
          try {
            result = fl.detectForVideo(vid, now);
          } catch {
            rafRef.current = requestAnimationFrame(detectLoop);
            return;
          }

          const faceDetected =
            result.faceLandmarks && result.faceLandmarks.length > 0;

          let lookingAway = false;

          if (faceDetected) {
            const landmarks = result.faceLandmarks[0];
            const { yaw, pitch } = computeHeadPose(landmarks);
            lookingAway =
              Math.abs(yaw) > YAW_THRESHOLD || Math.abs(pitch) > PITCH_THRESHOLD;
          } else {
            // No face = looking away
            lookingAway = true;
          }

          // Timer logic
          if (lookingAway) {
            if (lookAwayStartRef.current === null) {
              lookAwayStartRef.current = now;
            }
            const elapsed = now - lookAwayStartRef.current;
            if (elapsed >= lookAwayThresholdMs && !attentionLostRef.current) {
              attentionLostRef.current = true;
              setState((s) => ({
                ...s,
                isFaceDetected: !!faceDetected,
                isLookingAway: true,
                attentionLost: true,
              }));
              onAttentionLostRef.current?.();
            } else {
              setState((s) => ({
                ...s,
                isFaceDetected: !!faceDetected,
                isLookingAway: true,
              }));
            }
          } else {
            lookAwayStartRef.current = null;
            if (attentionLostRef.current) {
              attentionLostRef.current = false;
              setState((s) => ({
                ...s,
                isFaceDetected: true,
                isLookingAway: false,
                attentionLost: false,
              }));
              onAttentionRegainedRef.current?.();
            } else {
              setState((s) => ({
                ...s,
                isFaceDetected: true,
                isLookingAway: false,
              }));
            }
          }

          rafRef.current = requestAnimationFrame(detectLoop);
        }

        detectLoop();
      } catch (err) {
        if (!cancelled) {
          setState({
            status: "error",
            isFaceDetected: false,
            isLookingAway: false,
            attentionLost: false,
            errorMessage: "Failed to initialize face detection",
            stream: null,
          });
          console.error("FaceLandmarker init error:", err);
        }
      }
    }

    init();

    return () => {
      cancelled = true;
      cleanup();
    };
  }, [enabled, lookAwayThresholdMs, cleanup]);

  return state;
}
