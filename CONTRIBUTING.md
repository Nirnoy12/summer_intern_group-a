Contributing to the LMS Gamified Ingestion Platform

First off, welcome to the team! We are thrilled to have you here. This document outlines the process for contributing to our platform. Following these guidelines ensures that our codebase stays clean, our team avoids merge conflicts, and we can move fast.

🧠 Core Philosophy

Never push directly to main. All work happens in feature branches on your personal fork.

Keep Pull Requests (PRs) small and focused. One feature/bug per PR.

Communicate. If you're stuck, ask in the team chat.

🔄 The Development Workflow

We use a strict Fork and Pull Request workflow.

1. Sync Your Fork (Crucial)

Before starting any new work, you must sync your local main branch with the team's official main branch.

git checkout main
git fetch upstream
git merge upstream/main
git push origin main


2. Create a Feature Branch

Always create a new branch from your updated main branch. Use the following naming conventions:

feature/short-description (e.g., feature/login-ui, feature/youtube-ingestion)

fix/short-description (e.g., fix/db-connection, fix/button-alignment)

chore/short-description (e.g., chore/update-readme, chore/add-dependencies)

git checkout -b feature/your-feature-name


3. Commit Your Changes

Write clear, concise commit messages using Conventional Commits.

Format: <type>(<scope>): <description>
Examples:

feat(frontend): add interactive progress bar to dashboard

fix(backend): resolve unique constraint error on user registration

docs: update setup instructions for windows users

chore(frontend): install tailwindcss and lucide-react

4. Push and Open a Pull Request

Push your branch to your personal fork:

git push -u origin feature/your-feature-name


Then, go to the original team repository on GitHub and click "Compare & pull request".

📋 Pull Request (PR) Guidelines

When opening a PR, please ensure you:

Describe the changes: What did you add, fix, or remove?

Link the issue: If this PR solves a specific task or issue, mention it.

Keep it focused: Don't mix backend database migrations with frontend UI tweaks in the same PR unless they are strictly dependent.

Wait for review: Another team member or the Tech Lead must review and approve your code before it can be merged.

💻 Coding Standards

Backend (Python / FastAPI)

We use Python 3.10+.

Type Hints: Always use Python type hints for function arguments and return types.

Database: All database interactions must use SQLModel. Do not write raw SQL queries.

Environment Variables: Never hardcode passwords or API keys. Always use os.getenv() and the .env file.

Frontend (React / TypeScript)

We use TypeScript. Avoid using any type whenever possible. Define interfaces/types for your data.

Components: Use functional components and React Hooks (useState, useEffect).

Styling: We use Tailwind CSS. Avoid inline styles (style={{...}}) unless absolutely necessary for dynamic values.

UI Components: We rely on Shadcn UI and Lucide React icons for a consistent design system.

🚀 Need Help Setting Up?

If you haven't set up the project on your local machine yet, please read the README.md for step-by-step instructions on running the FastAPI backend and React frontend.