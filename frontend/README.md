# LMS Gamified Platform — Frontend Documentation

Welcome to the frontend of the Gamified Learning Management System (LMS). This application is a modern, responsive, and glassmorphic single-page web app built on **React 19** and **Vite**, featuring interactive game mechanics, smooth micro-animations, and real-time webcam attention tracking.

---

## 🛠️ Tech Stack

- **Framework**: [React 19](https://react.dev/) + [Vite](https://vite.dev/) (fast builds & HMR)
- **Language**: TypeScript (strict type safety)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/) + Modular Vanilla CSS system (`src/styles/`)
- **Icons & Animations**: [Lucide React](https://lucide.dev/) + [Framer Motion](https://www.framer.com/motion/)
- **Components**: Customized `shadcn/ui` UI primitives (`src/ui/`)
- **Computer Vision**: [MediaPipe Face Mesh](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker) (FaceLandmarker task compiled to WebAssembly)
- **HTTP Client**: [Axios](https://axios-http.com/)

---

## 📁 Source Code Map (`src/`)

```
frontend/src/
├── auth/                         # 🔐 FEATURE: Authentication
│   ├── auth.ts                   #   Axios instance with token interceptors
│   ├── AuthContext.tsx           #   React context (token state, login, logout)
│   ├── LoginForm.tsx             #   Modular Login Form Component
│   ├── LoginPage.tsx             #   /login route page
│   ├── RegisterForm.tsx          #   Modular Register Form Component
│   └── RegisterPage.tsx          #   /register route page
│
├── dashboard/                    # 📊 FEATURE: Learning Dashboard
│   ├── CourseCard.tsx            #   Modular Course Card Component
│   ├── DashboardPage.tsx         #   /dashboard route page
│   ├── ImportModal.tsx           #   YouTube Playlist Import Modal
│   ├── RemoveCourseModal.tsx     #   Course Removal Confirmation Modal
│   ├── StatsBar.tsx              #   User XP, Level, and Streak Bar
│   └── useDashboardData.ts       #   Custom hook for dashboard state
│
├── course-player/                # 🎬 FEATURE: Interactive Course Player
│   ├── CoursePlayerPage.tsx      #   /playlist/:id main workspace
│   ├── PlayerControls.tsx        #   Video play/pause & skip controls
│   ├── PlayerSidebar.tsx         #   Video list & quiz navigation sidebar
│   ├── WebcamPermissionGate.tsx  #   Webcam permission interface
│   ├── AttentionOverlay.tsx      #   Distraction alert overlay
│   ├── CameraPip.tsx             #   Picture-in-picture webcam feedback
│   ├── useCoursePlayer.ts        #   Custom hook for course player state
│   │
│   ├── proctoring/               #   🤖 AI Proctoring Subsystem
│   │   ├── headPose.ts           #   Head pose (Yaw/Pitch) calculator
│   │   ├── initFaceLandmarker.ts #   MediaPipe FaceLandmarker loader
│   │   └── useProctoring.ts      #   Gaze tracking & distraction hook
│   │
│   ├── quiz/                     #   🧩 Quiz Subsystem
│   │   ├── QuizQuestion.tsx      #   Question & multiple-choice component
│   │   ├── QuizResult.tsx        #   Score breakdown & XP earned component
│   │   └── QuizView.tsx          #   Quiz container & submission handler
│   │
│   └── ytPlayer/                 #   🎥 YouTube IFrame Integration
│       ├── loadYouTubeAPI.ts     #   Async IFrame API loader
│       ├── types.ts              #   Player TypeScript types
│       └── useYouTubePlayer.ts   #   YouTube player controls hook
│
├── landing/                      # 🏠 FEATURE: Landing Page
│   ├── FeaturesSection.tsx       #   Platform features grid
│   ├── HeroSection.tsx           #   Hero headline & call to action
│   ├── HowItWorksSection.tsx     #   3-step workflow demonstration
│   └── LandingPage.tsx           #   / public home page
│
├── styles/                       # 🎨 Modular CSS Design System
│   ├── animations.css            #   Custom animations & keyframes
│   ├── base.css                  #   Base CSS reset & variables
│   ├── components.css            #   Glassmorphism & component rules
│   └── utilities.css             #   Helper utility classes
│
├── theme/                        # 🌗 Theme Engine
│   ├── AnimatedBackground.tsx    #   Interactive background container
│   ├── ThemeToggle.tsx           #   Dark / light mode toggle
│   ├── useTheme.ts               #   Theme state hook
│   └── animatedBg/               #   Particle Animation Subsystem
│       ├── constants.ts          #   Particle constants
│       └── useParticles.ts       #   Interactive particle physics hook
│
├── ui/                           # 🧱 Base UI Primitives (shadcn)
│   ├── avatar.tsx
│   ├── badge.tsx
│   ├── button.tsx
│   ├── card.tsx
│   ├── input.tsx
│   ├── label.tsx
│   ├── progress.tsx
│   └── separator.tsx
│
├── lib/                          # 🔧 Utilities
│   └── utils.ts                  #   Tailwind class merge helper (`cn`)
│
├── App.tsx                       # Root router configuration
├── main.tsx                      # React DOM entry point
└── index.css                     # Primary stylesheet & imports
```

---

## ⚙️ Key Technical Implementations

### 1. Web proctoring via MediaPipe FaceLandmarker (`useProctoring.ts`)
Tracks user attention using webcam frames:
- Processed via WebAssembly-based **Face Mesh** at ~15fps.
- Calculates head pose (**yaw** and **pitch** angles).
- Triggers `onAttentionLost` if distracted for >3 seconds, pausing video playback and presenting an attention warning overlay.

### 2. YouTube IFrame API Integration (`useYouTubePlayer.ts`)
- Injects YouTube IFrame API dynamically into the DOM.
- Connects video controls with proctoring callbacks to automatically pause video when distraction is detected.

### 3. Gamification & Course Ingestion
- **Level & XP System**: Tracks XP per video completion (50 XP) and quiz attempts.
- **Playlist Ingestion**: Parses YouTube playlist URLs (`list=...`), fetches video metadata, and constructs structured course tracks.

---

## 🚀 Build & Verification Commands

```bash
# Install dependencies
npm install

# Start local dev server
npm run dev

# Compile for production
npm run build
```
