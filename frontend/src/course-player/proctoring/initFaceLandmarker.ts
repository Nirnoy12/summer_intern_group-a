import { FaceLandmarker, FilesetResolver } from "@mediapipe/tasks-vision";

export async function initFaceLandmarker(cancelledRef: { current: boolean }): Promise<FaceLandmarker | null> {
  const vision = await FilesetResolver.forVisionTasks(
    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
  );
  if (cancelledRef.current) return null;

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

  if (cancelledRef.current) {
    faceLandmarker.close();
    return null;
  }

  return faceLandmarker;
}

export function createHiddenVideoElement(stream: MediaStream): HTMLVideoElement {
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
  return video;
}
