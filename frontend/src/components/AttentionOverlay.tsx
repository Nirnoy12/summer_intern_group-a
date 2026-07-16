import { motion, AnimatePresence } from "framer-motion";
import { EyeOff } from "lucide-react";

interface AttentionOverlayProps {
  visible: boolean;
}

export function AttentionOverlay({ visible }: AttentionOverlayProps) {
  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.4 }}
          className="attention-overlay"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 10 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="attention-overlay-card"
          >
            {/* Animated eye icon */}
            <div className="attention-overlay-icon">
              <motion.div
                animate={{
                  scale: [1, 1.15, 1],
                  opacity: [0.8, 1, 0.8],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              >
                <EyeOff className="w-10 h-10" />
              </motion.div>
            </div>

            {/* Message */}
            <h3 className="attention-overlay-title">Attention Lost</h3>
            <p className="attention-overlay-description">
              Please look at the screen to resume the video.
            </p>

            {/* Animated scanning line */}
            <div className="attention-scan-line" />
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
