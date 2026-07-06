Project Setup

Step 1: Fork and Clone the Repository

Click the "Fork" button in the top right corner of the main GitHub repository to create a copy in your own GitHub account.

Open your terminal and clone your fork to your local machine:

git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
cd YOUR_REPOSITORY_NAME


Step 2: Backend Setup (FastAPI)

Open a new terminal window and follow these steps to start the Python server.

Navigate to the backend folder:

cd backend


Create a Virtual Environment:

python -m venv venv


Activate the Virtual Environment:

Windows (PowerShell): .\venv\Scripts\Activate

Mac / Linux: source venv/bin/activate
(You should now see (venv) at the start of your terminal line)

Install Dependencies:

pip install fastapi uvicorn sqlmodel sqlalchemy-cockroachdb "passlib[argon2]" python-dotenv python-jose python-multipart


Set up Environment Variables:

Create a file named exactly .env inside the backend folder.

Ask the Tech Lead for the CockroachDB database credentials.

Paste them into the file like this:

# CRITICAL: The URL must start with cockroachdb:// (NOT postgresql://)
# CRITICAL FOR WINDOWS: The URL must end with &sslrootcert=system
DATABASE_URL=cockroachdb://<username>:<password>@<host>:26257/defaultdb?sslmode=verify-full&sslrootcert=system
SECRET_KEY=my-super-secret-mvp-key-for-jwt-tokens


Run the Backend Server:

uvicorn main:app --reload


The backend is now running at: http://127.0.0.1:8000
You can view the interactive API docs at: http://127.0.0.1:8000/docs

Step 3: Frontend Setup (React + Vite)

Open a second, separate terminal window and follow these steps to start the UI.

Navigate to the frontend folder:

cd frontend


Install Node Modules:

npm install


Run the Development Server:

npm run dev


The frontend is now running at: http://localhost:5173

Step 4: Verify Everything is Working

To prove your local setup is perfect:

Open http://127.0.0.1:8000/docs in your browser.

Open the POST /api/auth/register endpoint.

Click "Try it out", enter a test email and password, and click "Execute".

If you receive a 200 OK response with a User ID, your database connection is working perfectly! You are cleared to start developing.