# LMS Gamified Platform — Frontend Documentation

Welcome to the frontend of the Gamified Learning Management System (LMS). This application is a modern, responsive, and glassmorphic single-page web app built on **React 19** and **Vite**, featuring interactive game mechanics, smooth micro-animations, and real-time webcam attention tracking.

---

## 🛠️ Tech Stack

- **Framework**: [React 19](https://react.dev/) + [Vite](https://vite.dev/) (fast builds & HMR)
- **Language**: TypeScript (type safety)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/) (modern CSS framework)
- **Icons & Animations**: [Lucide React](https://lucide.dev/) + [Framer Motion](https://www.framer.com/motion/)
- **Components**: Inspired by `shadcn/ui` custom styling
- **Computer Vision**: [MediaPipe Face Mesh](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker) (FaceLandmarker task compiled to WebAssembly)
- **HTTP Client**: [Axios](https://axios-http.com/)

---

## 📂 Source Code Map (`src/`)

```
frontend/src/
├── api/              # API helpers and configurations
├── assets/           # Static files, global stylesheets
├── auth/             # LoginPage, RegisterPage, AuthContext, and Axios API configurations
├── course-player/    # Course player workspace, including:
│   ├── CoursePlayerPage.tsx      # Main layout for watching lessons and tracking progress
│   ├── QuizView.tsx              # Renders the dynamic quizzes generated from transcriptions
│   ├── AttentionOverlay.tsx      # Warning overlay triggered when looking away
│   ├── WebcamPermissionGate.tsx  # Initial permission interface for webcam access
│   ├── useYouTubePlayer.ts       # Hook wrapping YouTube Player API
│   └── useProctoring.ts          # Hook running MediaPipe face mesh proctoring loop
├── dashboard/        # DashboardPage (User stats, course roadmaps, and course ingestion)
├── landing/          # LandingPage, Navbar, and Footer
├── lib/              # Utility configurations (e.g., clsx, tailwind-merge)
├── theme/            # ThemeContext, ThemeToggle, and AnimatedBackground components
├── types/            # App-wide TypeScript definitions
├── ui/               # Standard UI components (Card, Button, Progress, Badge, Toast)
├── App.tsx           # Client-side router configuration (React Router Dom)
└── main.tsx          # App entrypoint
```

---

## ⚙️ Key Technical Implementations

### 1. Web proctoring via MediaPipe FaceLandmarker (`useProctoring.ts`)
To increase accountability, the application includes a webcam-based proctoring system that tracks user attention:
* It requests access to the user's webcam and feeds the stream to a hidden `<video>` element.
* Every ~66ms (throttled to ~15fps for low CPU consumption), MediaPipe's WebAssembly-based **Face Mesh** model processes the frame.
* It estimates head pose by calculating the horizontal (**yaw**) and vertical (**pitch**) ratios of the nose tip relative to key facial landmarks (nose bridge, eye edges, forehead, and chin).
* If the user turns their head past the threshold (yaw > 25° or pitch > 25°), or if no face is detected in the frame, the "look away" timer starts.
* If attention is lost for more than **3 seconds**, an attention-loss callback is triggered, pausing the course video and popping up a glassmorphic attention warning overlay (`AttentionOverlay.tsx`).

### 2. YouTube IFrame API Integration (`useYouTubePlayer.ts`)
* Injects the standard YouTube IFrame API script dynamically into the DOM.
* Connects a custom controller ref to the YouTube video iframe.
* Exposes utility callbacks to parent components (`play`, `pause`, `seekTo`, `getCurrentTime`, `getDuration`).
* Automatically pauses the video playback when the user gets distracted (notified by the proctoring hook).

### 3. Gamification Mechanics & Dashboard
* **Streaks**: Refreshed dynamically on login. If the user completes a video on consecutive days, the streak count increases.
* **XP & Level Progression**: Displays animated progress bars showing the remaining XP needed to level up. XP is earned by completing lessons (100 XP) and scoring high on quizzes (300 XP).
* **Course Ingestion**: Users can paste any public YouTube playlist URL directly. The frontend parses the `list=` URL parameter and posts it to the backend to instantly ingest and build the learning path.

---

## 🚀 Getting Started

1. Set up dependencies:
   ```bash
   npm install
   ```
2. Start the Vite server locally:
   ```bash
   npm run dev
   ```
3. Compile for production:
   ```bash
   npm run build
   ```
4. Verify code linting:
   ```bash
   npm run lint
   ```
