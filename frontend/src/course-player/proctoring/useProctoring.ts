import { useEffect, useRef, useState, useCallback } from "react";
import { FaceLandmarker } from "@mediapipe/tasks-vision";
import type { FaceLandmarkerResult } from "@mediapipe/tasks-vision";
import type { ProctoringState, UseProctoringOptions } from "./headPose";
import { computeHeadPose, YAW_THRESHOLD, PITCH_THRESHOLD } from "./headPose";
import { initFaceLandmarker, createHiddenVideoElement } from "./initFaceLandmarker";

export function useProctoring({ enabled, lookAwayThresholdMs = 3000, onAttentionLost, onAttentionRegained }: UseProctoringOptions): ProctoringState {
  const [state, setState] = useState<ProctoringState>({ status: "idle", isFaceDetected: false, isLookingAway: false, attentionLost: false, stream: null });

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const faceLandmarkerRef = useRef<FaceLandmarker | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const rafRef = useRef<number>(0);
  const lookAwayStartRef = useRef<number | null>(null);
  const attentionLostRef = useRef(false);
  const onAttentionLostRef = useRef(onAttentionLost);
  const onAttentionRegainedRef = useRef(onAttentionRegained);
  const lastDetectionTimeRef = useRef<number>(0);

  onAttentionLostRef.current = onAttentionLost;
  onAttentionRegainedRef.current = onAttentionRegained;

  const cleanup = useCallback(() => {
    if (rafRef.current) { cancelAnimationFrame(rafRef.current); rafRef.current = 0; }
    if (streamRef.current) { streamRef.current.getTracks().forEach((t) => t.stop()); streamRef.current = null; }
    if (videoRef.current) { videoRef.current.srcObject = null; videoRef.current.remove(); videoRef.current = null; }
    if (faceLandmarkerRef.current) { faceLandmarkerRef.current.close(); faceLandmarkerRef.current = null; }
  }, []);

  useEffect(() => {
    if (!enabled) { cleanup(); setState({ status: "idle", isFaceDetected: false, isLookingAway: false, attentionLost: false, stream: null }); return; }

    const cancelledRef = { current: false };

    async function init() {
      setState((s) => ({ ...s, status: "requesting" }));
      let stream: MediaStream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { width: 320, height: 240, facingMode: "user" } });
      } catch (err) {
        if (!cancelledRef.current) {
          const isDenied = err instanceof DOMException && (err.name === "NotAllowedError" || err.name === "PermissionDeniedError");
          setState({ status: isDenied ? "denied" : "error", isFaceDetected: false, isLookingAway: false, attentionLost: false, errorMessage: isDenied ? "Camera permission denied" : "Failed to access camera", stream: null });
        }
        return;
      }

      if (cancelledRef.current) { stream.getTracks().forEach((t) => t.stop()); return; }
      streamRef.current = stream;

      const video = createHiddenVideoElement(stream);
      videoRef.current = video;
      await video.play();
      if (cancelledRef.current) { cleanup(); return; }

      try {
        const faceLandmarker = await initFaceLandmarker(cancelledRef);
        if (!faceLandmarker || cancelledRef.current) return;
        faceLandmarkerRef.current = faceLandmarker;
        setState((s) => ({ ...s, status: "active", stream: streamRef.current }));

        function detectLoop() {
          if (cancelledRef.current) return;
          const now = performance.now();
          if (now - lastDetectionTimeRef.current < 66) { rafRef.current = requestAnimationFrame(detectLoop); return; }
          lastDetectionTimeRef.current = now;

          const vid = videoRef.current;
          const fl = faceLandmarkerRef.current;
          if (!vid || !fl || vid.readyState < 2) { rafRef.current = requestAnimationFrame(detectLoop); return; }

          let result: FaceLandmarkerResult;
          try { result = fl.detectForVideo(vid, now); } catch { rafRef.current = requestAnimationFrame(detectLoop); return; }

          const faceDetected = result.faceLandmarks && result.faceLandmarks.length > 0;
          let lookingAway = !faceDetected;
          if (faceDetected) {
            const { yaw, pitch } = computeHeadPose(result.faceLandmarks[0]);
            lookingAway = Math.abs(yaw) > YAW_THRESHOLD || Math.abs(pitch) > PITCH_THRESHOLD;
          }

          if (lookingAway) {
            if (lookAwayStartRef.current === null) lookAwayStartRef.current = now;
            const elapsed = now - lookAwayStartRef.current;
            if (elapsed >= lookAwayThresholdMs && !attentionLostRef.current) {
              attentionLostRef.current = true;
              setState((s) => ({ ...s, isFaceDetected: !!faceDetected, isLookingAway: true, attentionLost: true }));
              onAttentionLostRef.current?.();
            } else {
              setState((s) => ({ ...s, isFaceDetected: !!faceDetected, isLookingAway: true }));
            }
          } else {
            lookAwayStartRef.current = null;
            if (attentionLostRef.current) {
              attentionLostRef.current = false;
              setState((s) => ({ ...s, isFaceDetected: true, isLookingAway: false, attentionLost: false }));
              onAttentionRegainedRef.current?.();
            } else {
              setState((s) => ({ ...s, isFaceDetected: true, isLookingAway: false }));
            }
          }
          rafRef.current = requestAnimationFrame(detectLoop);
        }
        detectLoop();
      } catch (err) {
        if (!cancelledRef.current) {
          setState({ status: "error", isFaceDetected: false, isLookingAway: false, attentionLost: false, errorMessage: "Failed to initialize face detection", stream: null });
        }
      }
    }

    init();
    return () => { cancelledRef.current = true; cleanup(); };
  }, [enabled, lookAwayThresholdMs, cleanup]);

  return state;
}
