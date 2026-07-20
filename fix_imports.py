import os

replacements = {
    "@/components/ui": "@/ui",
    "@/pages/Login": "@/auth/LoginPage",
    "@/pages/Register": "@/auth/RegisterPage",
    "@/context/AuthContext": "@/auth/AuthContext",
    "@/services/auth": "@/auth/auth",
    "@/pages/Dashboard": "@/dashboard/DashboardPage",
    "@/pages/CoursePlayer": "@/course-player/CoursePlayerPage",
    "@/hooks/useYouTubePlayer": "@/course-player/useYouTubePlayer",
    "@/hooks/useProctoring": "@/course-player/useProctoring",
    "@/components/AttentionOverlay": "@/course-player/AttentionOverlay",
    "@/components/WebcamPermissionGate": "@/course-player/WebcamPermissionGate",
    "@/pages/Landing": "@/landing/LandingPage",
    "@/components/Navbar": "@/landing/Navbar",
    "@/components/Footer": "@/landing/Footer",
    "@/components/AnimatedBackground": "@/theme/AnimatedBackground",
    "@/components/ThemeToggle": "@/theme/ThemeToggle",
    "@/context/ThemeContext": "@/theme/ThemeContext",
    "./pages/Landing": "./landing/LandingPage",
    "./pages/Dashboard": "./dashboard/DashboardPage",
    "./pages/CoursePlayer": "./course-player/CoursePlayerPage",
    "./pages/Login": "./auth/LoginPage",
    "./pages/Register": "./auth/RegisterPage",
    "./context/AuthContext": "./auth/AuthContext",
    "./context/ThemeContext": "./theme/ThemeContext",
}

for root, _, files in os.walk("frontend/src"):
    for file in files:
        if file.endswith(".ts") or file.endswith(".tsx"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                
            for old, new in replacements.items():
                content = content.replace(old, new)
                
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
                
print("Imports updated!")
