import { motion } from "framer-motion";
import { Camera, ShieldAlert, ShieldCheck, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface WebcamPermissionGateProps {
  status: "idle" | "requesting" | "denied" | "error";
  errorMessage?: string;
  onRequestPermission: () => void;
}

export function WebcamPermissionGate({
  status,
  errorMessage,
  onRequestPermission,
}: WebcamPermissionGateProps) {
  const isDenied = status === "denied";
  const isError = status === "error";
  const isRequesting = status === "requesting";

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      className="webcam-gate"
    >
      <motion.div
        initial={{ opacity: 0, y: 20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="webcam-gate-card"
      >
        {/* Icon */}
        <div className={`webcam-gate-icon ${isDenied || isError ? "error" : ""}`}>
          {isDenied || isError ? (
            <ShieldAlert className="w-8 h-8" />
          ) : isRequesting ? (
            <Loader2 className="w-8 h-8 animate-spin" />
          ) : (
            <Camera className="w-8 h-8" />
          )}
        </div>

        {/* Title */}
        <h3 className="webcam-gate-title">
          {isDenied
            ? "Camera Access Required"
            : isError
            ? "Camera Error"
            : isRequesting
            ? "Requesting Access..."
            : "Enable Camera for Proctoring"}
        </h3>

        {/* Description */}
        <p className="webcam-gate-description">
          {isDenied ? (
            <>
              Camera access was denied. This course requires webcam-based
              attention monitoring to ensure active engagement. Please enable
              camera permissions in your browser settings and reload the page.
            </>
          ) : isError ? (
            <>
              {errorMessage ||
                "An error occurred while accessing your camera. Please check that your webcam is connected and try again."}
            </>
          ) : isRequesting ? (
            <>Please allow camera access in the browser prompt...</>
          ) : (
            <>
              This course uses AI-based attention monitoring to ensure you're
              actively engaging with the content. Your webcam will track your
              gaze to verify attention.
            </>
          )}
        </p>

        {/* Action button */}
        {!isRequesting && (
          <Button
            onClick={onRequestPermission}
            className="webcam-gate-button"
            variant={isDenied || isError ? "destructive" : "default"}
            disabled={isDenied}
          >
            {isDenied || isError ? (
              <>
                <ShieldAlert className="w-4 h-4 mr-2" />
                {isDenied ? "Permission Denied" : "Retry Access"}
              </>
            ) : (
              <>
                <ShieldCheck className="w-4 h-4 mr-2" />
                Grant Camera Access
              </>
            )}
          </Button>
        )}

        {/* Privacy notice */}
        <div className="webcam-gate-privacy">
          <ShieldCheck className="w-3.5 h-3.5 shrink-0" />
          <span>
            Your webcam feed is processed entirely on your device and is never
            sent to any server.
          </span>
        </div>
      </motion.div>
    </motion.div>
  );
}
