# 📅 AI Calendar Planner

**AI Calendar Planner** is an AI-powered task and scheduling application that turns natural-language requests into structured tasks and helps fit those tasks into a realistic calendar. It combines a **FastAPI backend, Streamlit interface, Google Gemini, a rule-based multi-day scheduling engine, SQLAlchemy persistence, and Google Calendar integration**.

Instead of manually breaking work into tasks and finding time for each one, a user can describe what they need to do, let the AI extract task details, and generate a schedule that accounts for deadlines, task priority, working hours, preferred work periods, breaks, and existing calendar events.

> **Project repository:** [Sanika-Gajarishi/AI-Calender-Planner](https://github.com/Sanika-Gajarishi/AI-Calender-Planner)

---

## Contents

- [Why this project?](#-why-this-project)
- [Features](#-features)
- [How it works](#-how-it-works)
- [Technology stack](#-technology-stack)
- [Architecture](#-architecture)
- [Project structure](#-project-structure)
- [Getting started](#-getting-started)
- [Google Calendar setup](#-google-calendar-setup)
- [Running the application](#-running-the-application)
- [API overview](#-api-overview)
- [Scheduling logic](#-scheduling-logic)
- [Database and migrations](#-database-and-migrations)
- [Testing](#-testing)
- [Configuration and security](#-configuration-and-security)
- [Known limitations](#-known-limitations)
- [Potential improvements](#-potential-improvements)
- [Author](#-author)

---

## 💡 Why this project?

Task lists show what needs to be done, but they do not always answer a more important question: **When should each task actually happen?**

AI Calendar Planner helps bridge that gap. It extracts useful details from natural-language requests, stores tasks, checks available time, and schedules work across multiple days. When Google Calendar is connected, existing events can be treated as busy periods and the generated schedule can be synchronized back to the calendar.

The project is intended as a practical demonstration of AI integration, backend API development, scheduling algorithms, database design, authentication, and third-party API integration.

---

## ✨ Features

### 🤖 1. Natural-language task creation

Describe a task in everyday language, for example:

> “Prepare for my Python interview by Friday. Spend about two hours on coding practice, make it high priority, and schedule it in the evening.”

The backend uses **Google Gemini (gemini-2.5-flash)** to extract structured task information, including:

- Title and description
- Priority: low, medium, or high
- Estimated duration in minutes
- Deadline, when one is clearly provided
- Preferred working period
- Category, such as work, study, interview, project, or personal

The extracted task is validated and saved to the database for the authenticated user. The task-understanding prompt is designed to interpret relative dates using the current application date and the user's timezone, and to avoid inventing deadlines when the request is ambiguous.

### 📋 2. Task management

Users can create and manage their tasks through the API and Streamlit interface. A task can include:

- Title and description
- Priority
- Deadline
- Estimated duration
- Category
- Notes
- Status
- Preferred time of day

Task endpoints support creating, listing, retrieving, updating, and deleting tasks. Tasks are associated with users, and task queries in the authenticated task routes are scoped to the signed-in user.

### 🧠 3. Intelligent multi-day scheduling

The scheduling engine allocates tasks into available working time across a requested range of days. It uses task priority and deadline urgency when deciding what to schedule first.

Scheduling takes account of configured working hours, preferred time windows, existing busy periods, task duration, deadlines, break duration, and daily scheduling limits. Long tasks can be split into multiple scheduled blocks when one free period is not long enough.

The engine also handles tasks that cannot fit into the available time rather than assuming every task can always be scheduled.

### 📅 4. Google Calendar integration

The Google Calendar integration can:

- Check connection status
- Retrieve events over a chosen date range
- Identify existing events that block time
- Use calendar events when checking scheduling conflicts
- Create calendar events for generated schedule blocks
- Update or delete events created by the planner
- Synchronize a generated schedule with Google Calendar

This integration uses Google OAuth credentials and the Google Calendar API. Calendar access is optional for local development of the task-management and scheduling functionality, but is required for the connected-calendar workflows.

### 💬 5. AI Calendar Agent

The agent-style chat interface lets users request calendar and scheduling actions in natural language.

The agent is built using LangChain's agent tools and a Google Gemini chat model. Its tools support actions such as:

- Listing pending tasks
- Checking an appointment for conflicts with Google Calendar events
- Finding available time periods
- Rescheduling a scheduled task
- Generating an optimized schedule
- Synchronizing the schedule with Google Calendar

For conflict-related questions, the agent is instructed to check the actual calendar before responding. It should not claim that a conflict has been checked or that a task has been rescheduled unless the corresponding tool has been used.

### 🔐 6. Authentication

The API provides registration and login endpoints. Passwords are hashed with bcrypt, and successful login returns a signed JWT access token. Protected endpoints use the token supplied in the HTTP Authorization header.

Example header:

~~~http
Authorization: Bearer YOUR_ACCESS_TOKEN
~~~

The current token lifetime is configured in the backend security module.

### ⚙️ 7. Scheduling preferences

The data model supports preferences that influence schedule generation, such as:

- Working-day start and end times
- Preferred work period
- Maximum daily working hours
- Break duration
- Preferred task length
- Timezone

See [Known limitations](#-known-limitations) for the current status of the preferences API.

### 🖥️ 8. Streamlit user interface

The frontend includes views/components for:

- Registration and login
- AI-assisted task creation
- Task lists and task deletion
- Schedule generation
- Calendar event viewing
- Google Calendar connection and synchronization
- AI Calendar Agent chat

The Streamlit frontend communicates with the FastAPI backend through a dedicated API client.

---

## 🔄 How it works

### Task creation and scheduling workflow

~~~text
User describes a task in natural language
                  |
                  v
        FastAPI receives the request
                  |
                  v
       Gemini extracts task details
                  |
                  v
       Validate and save the task
                  |
                  v
 Load tasks, preferences, and busy periods
                  |
                  v
      Prioritize tasks by urgency
                  |
                  v
     Find free working-time windows
                  |
                  v
 Allocate tasks and breaks across days
                  |
                  v
       Persist scheduled time blocks
                  |
                  v
 Optional: sync schedule to Google Calendar
~~~

### Conflict-checking workflow

~~~text
User asks whether a time conflicts
                  |
                  v
      Agent calls the conflict tool
                  |
                  v
     Read events from Google Calendar
                  |
                  v
       Compare overlapping periods
                  |
             +----+----+
             |         |
          Conflict   No conflict
             |         |
             v         v
     Explain overlap   Report result
     and search for
     available times
~~~

---

## 🧰 Technology stack

| Area | Technologies |
|---|---|
| Language | Python |
| Backend API | FastAPI, Uvicorn |
| Frontend | Streamlit |
| LLM integration | Google Gemini API, Google Gen AI SDK |
| Agent framework | LangChain, LangChain Google GenAI |
| Scheduling | Python scheduling and time-slot allocation modules |
| Database ORM | SQLAlchemy |
| Schema migrations | Alembic |
| Validation | Pydantic |
| Authentication | JWT, bcrypt, Passlib |
| Calendar integration | Google Calendar API, Google OAuth |
| HTTP integration | Requests |
| Testing | Pytest |

---

## 🏗️ Architecture

~~~text
                   ┌─────────────────────────┐
                   │   Streamlit Frontend    │
                   │ Tasks · Schedule · Chat │
                   └────────────┬────────────┘
                                │ HTTP
                                v
                   ┌─────────────────────────┐
                   │      FastAPI API        │
                   │ Auth · Tasks · Schedule │
                   │ AI · Calendar · Agent   │
                   └──────┬───────────┬──────┘
                          │           │
             ┌────────────v───┐   ┌───v────────────────┐
             │ SQLAlchemy ORM │   │ AI / Agent Services│
             │ Users, Tasks,  │   │ Gemini + LangChain │
             │ Preferences,   │   └────────────────────┘
             │ Schedule Blocks│
             └────────────────┘
                          │
                 ┌────────v─────────┐
                 │ Scheduling Engine│
                 │ Priority · Time  │
                 │ Slots · Deadlines│
                 │ Breaks · Busy    │
                 └────────┬─────────┘
                          │
                 ┌────────v─────────┐
                 │ Google Calendar  │
                 │ Read / Create /  │
                 │ Update / Delete  │
                 └──────────────────┘
~~~

---

## 📂 Project structure

~~~text
AI-Calender-Planner/
├── backend/
│   ├── app/
│   │   ├── agents/              # Agent setup and tools
│   │   ├── api/                 # FastAPI routers
│   │   ├── core/                # Settings, security, timezone helpers
│   │   ├── database/            # SQLAlchemy base and DB connection
│   │   ├── integrations/        # Google OAuth and Calendar API
│   │   ├── models/              # SQLAlchemy models
│   │   ├── scheduler/           # Time slots and scheduling algorithms
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── services/            # AI, tasks, scheduling, auth, agent services
│   │   ├── tools/               # Agent tools
│   │   └── main.py              # FastAPI application entry point
│   ├── alembic/
│   │   └── versions/            # Database migration revisions
│   ├── tests/                   # Automated tests
│   ├── requirements.txt
│   └── alembic.ini
├── frontend/
│   ├── components/
│   │   ├── agent_chat.py
│   │   ├── calendar_view.py
│   │   ├── sidebar.py
│   │   ├── task_form.py
│   │   └── task_list.py
│   ├── api_client.py            # Calls the FastAPI backend
│   ├── app.py                   # Streamlit app
│   └── config.py                # Backend API URL
└── README.md
~~~

---

## 🚀 Getting started

### Prerequisites

- Python 3.10 or newer is recommended.
- A Google Gemini API key for AI task extraction and agent responses.
- Google Calendar OAuth credentials if you want to use Google Calendar features.
- Git to clone the repository.

### 1. Clone the repository

~~~bash
git clone https://github.com/Sanika-Gajarishi/AI-Calender-Planner.git
cd AI-Calender-Planner
~~~

### 2. Create and activate a virtual environment

**Windows PowerShell**

~~~powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
~~~

If PowerShell blocks activation, use the appropriate execution policy for your environment or activate the environment from Command Prompt:

~~~bat
.venv\Scripts\activate.bat
~~~

**macOS / Linux**

~~~bash
python3 -m venv .venv
source .venv/bin/activate
~~~

### 3. Install dependencies

From the repository root:

~~~bash
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
~~~

The same environment can be used for both the backend and the Streamlit frontend.

### 4. Configure the backend environment

Create a file named **backend/.env**. The backend loads configuration from environment variables and a .env file.

Example for a local SQLite database:

~~~env
GEMINI_API_KEY=replace_with_your_gemini_api_key
DATABASE_URL=sqlite:///./ai_calendar_planner.db
~~~

The database URL is a SQLAlchemy connection string. For a shared or production environment, configure a suitable database such as PostgreSQL and supply the corresponding connection URL.

Do not commit this file or put actual API keys, passwords, or OAuth tokens in source control.

### 5. Start the backend

~~~bash
cd backend
uvicorn app.main:app --reload
~~~

The FastAPI API should start at:

- API root: http://127.0.0.1:8000/
- Health check: http://127.0.0.1:8000/health
- Interactive API documentation: http://127.0.0.1:8000/docs
- Alternative API documentation: http://127.0.0.1:8000/redoc

The application creates tables from the SQLAlchemy models during startup. Alembic migration files are also included for schema management.

### 6. Start the Streamlit frontend

Open a second terminal, activate the same virtual environment, then run:

~~~bash
cd frontend
streamlit run app.py
~~~

The Streamlit interface will print its local URL in the terminal, usually http://localhost:8501.

The backend URL is currently configured in **frontend/config.py** as:

~~~python
API_BASE_URL = "http://127.0.0.1:8000"
~~~

Change this setting when connecting the frontend to a different backend host.

---

## 🗓️ Google Calendar setup

Google Calendar integration requires a Google Cloud project and OAuth client credentials.

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select a project.
3. Enable the **Google Calendar API** for the project.
4. Configure the OAuth consent screen and add your Google account as a test user if the app is in testing mode.
5. Create an OAuth client ID for a **Desktop app** and download its JSON file.
6. Create the directory **backend/credentials/**.
7. Place the downloaded file at **backend/credentials/google_client_secret.json**.
8. Keep the downloaded credentials private and do not commit them.
9. Start the backend and use the application's Google Calendar connection action.

The integration uses the Google Calendar scope:

~~~text
https://www.googleapis.com/auth/calendar
~~~

On the first authorization, the local OAuth flow opens a browser for consent and stores a token at **backend/token.json**. Keep this token private. If access is revoked or the token expires, authorization may need to be repeated.

Because the current implementation uses local OAuth credentials and a token file, treat this as a local-development setup rather than a production multi-user OAuth architecture.

---

## 🔌 API overview

Use the interactive documentation at **http://127.0.0.1:8000/docs** for request schemas, response formats, and try-it-out testing.

### Health

| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | Confirm that the API is running |
| GET | /health | Basic health check |

### Authentication

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /auth/register | Register an account |
| POST | /auth/login | Authenticate and receive a JWT |

Example registration request:

~~~json
{
  "name": "Example User",
  "email": "user@example.com",
  "password": "use_a_strong_password"
}
~~~

Example login request:

~~~json
{
  "email": "user@example.com",
  "password": "use_a_strong_password"
}
~~~

Use the returned access token in the Authorization header for protected endpoints.

### Tasks

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /tasks/ | Create a task manually |
| GET | /tasks/ | List the current user's tasks |
| GET | /tasks/{task_id} | Retrieve a task |
| PUT | /tasks/{task_id} | Update a task |
| DELETE | /tasks/{task_id} | Delete a task and its associated scheduled blocks |

### AI task creation

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /ai/create-task | Extract task details from natural language and save the task |

Example request:

~~~json
{
  "text": "Prepare for my Python interview by Friday. I need 120 minutes and prefer evenings."
}
~~~

### Scheduling

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /schedule?start_date=YYYY-MM-DD&number_of_days=7 | Retrieve saved scheduled blocks |
| POST | /schedule/generate?start_date=YYYY-MM-DD&number_of_days=7 | Generate a schedule |
| POST | /schedule/sync-google?start_date=YYYY-MM-DD&number_of_days=7 | Synchronize the scheduled blocks to Google Calendar |

The number of days defaults to 7 when omitted where supported by the endpoint.

### Google Calendar

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /calendar/status | Check the connection status |
| POST | /calendar/connect | Start the Calendar connection flow |
| GET | /calendar/events?days=7 | Retrieve events for the requested number of days |

### AI Calendar Agent

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /agent/chat?message=YOUR_MESSAGE | Send a natural-language message to the agent |

The chat endpoint accepts the message as a query parameter. It can return an agent response and, for task-list requests, a list of pending tasks.

### Preferences

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /preferences/ | Create scheduling preferences |
| GET | /preferences/ | Retrieve scheduling preferences |

**Important:** the current preferences endpoints use a fixed user ID internally rather than deriving the user from the authenticated JWT. Review the [Known limitations](#-known-limitations) section before using these endpoints with multiple users.

---

## 🧠 Scheduling logic

The scheduling implementation is organized into focused modules under **backend/app/scheduler/**.

### Task prioritization

Tasks are ordered using a score based on priority and deadline urgency. High-priority tasks receive a higher base score than medium- or low-priority tasks. Tasks with approaching deadlines receive an additional urgency score, with larger boosts for deadlines within the next day, three days, or week.

### Free-time allocation

The scheduler constructs working windows for the requested days, reads calendar events as busy periods, and subtracts busy intervals to find free slots. It then allocates work into eligible slots, considering task length, deadline, and preferred time of day.

### Breaks and multiple days

Break duration is configurable. The multi-day scheduler can allocate a task over more than one free block, and it tracks tasks that cannot be placed in the available windows.

### Persistence and calendar sync

Generated blocks are stored in the **scheduled_blocks** table with start time, end time, duration, and an optional Google Calendar event ID. That identifier allows the integration to associate locally saved blocks with events created in Google Calendar.

---

## 🗃️ Database and migrations

SQLAlchemy models are defined under **backend/app/models/**. The principal entities include:

- **User** — account identity, password hash, Google Calendar connection marker, and timezone.
- **Task** — task details, priority, deadline, estimated duration, category, status, notes, and preferred time.
- **UserPreference** — work hours, preferred work period, daily limits, break duration, preferred task length, and timezone.
- **ScheduledBlock** — allocated task time blocks and their associated Google Calendar event IDs.

A database URL is required through **DATABASE_URL**. An example local value is:

~~~env
DATABASE_URL=sqlite:///./ai_calendar_planner.db
~~~

The application initializes its SQLAlchemy tables on startup. Alembic configuration and revision files are included in **backend/alembic/** for migrations. When changing the data model, create and review migrations as part of the development workflow rather than relying only on automatic table creation.

---

## 🧪 Testing

The backend contains Pytest tests for areas such as:

- AI task creation
- Database behavior
- Gemini integration
- Google Calendar integration
- Scheduler behavior

Run the tests from the **backend/** directory with the virtual environment activated:

~~~bash
pytest
~~~

Some integration tests may require a configured database, Gemini API key, or Google OAuth credentials. Run external-service tests only after configuring the required credentials, and avoid committing test tokens or secrets.

---

## 🔐 Configuration and security

This repository is set up for development and should be reviewed before public deployment.

- Keep **GEMINI_API_KEY**, Google OAuth client secrets, token files, and database credentials private.
- Use environment-specific settings and a strong, externally configured JWT signing secret.
- Restrict CORS origins and allowed hosts appropriately for the deployment environment.
- Serve production traffic over HTTPS.
- Use a production-ready database and configure backups.
- Review access checks for every user-specific route.
- Use separate OAuth credentials or securely stored per-user tokens for a multi-user deployment.
- Configure sensible request limits, logging, error handling, and rate limiting.
- Do not expose database contents, access tokens, or sensitive exception details to users.

---

## ⚠️ Known limitations

These are important implementation details to understand when running or extending the project:

1. **Preferences API scoping:** the current preference routes use user ID 1 instead of the authenticated user's ID. This needs to be corrected before relying on preferences in a multi-user deployment.
2. **Google OAuth storage:** the integration stores OAuth credentials in a local token file, rather than managing a separate securely stored token for each user. This is suitable for a local demo but not a complete multi-user authorization design.
3. **JWT signing secret:** the current security module defines a placeholder signing secret in code. Move it to secure environment configuration and rotate it before any deployment.
4. **Frontend API URL:** the Streamlit client currently points to the local backend URL. Configure it for your target environment before deployment.
5. **Calendar timezone handling:** review timezone behavior end-to-end before using the application across regions. Calendar event creation currently uses an explicit Asia/Kolkata timezone in the Google Calendar integration.
6. **Generated schedule quality:** the scheduling engine uses deterministic prioritization and time-slot allocation heuristics; it is not a mathematical guarantee of an optimal schedule. Verify generated schedules before relying on them for critical commitments.
7. **Third-party availability:** AI task extraction and calendar features depend on external APIs and their credentials, connectivity, permissions, quotas, and availability.

---

## 🚀 Potential improvements

Possible next steps for evolving the project include:

- Scope preference APIs to the authenticated user and add preference update support.
- Move the JWT signing secret into environment configuration.
- Implement per-user Google OAuth token storage and token revocation.
- Add automated tests for multi-user access control and timezones.
- Add schedule explanations showing why each task received a particular time slot.
- Add schedule conflict detection for overlapping locally generated blocks.
- Add reminders and notifications for approaching deadlines.
- Add a calendar-style timeline or weekly visualization.
- Add Docker-based local development and deployment.
- Add CI workflows for linting, tests, and migration checks.
- Add production logging, monitoring, rate limiting, and deployment documentation.

---

## 👩‍💻 Author

**Sanika Gajarishi**

- GitHub: [Sanika-Gajarishi](https://github.com/Sanika-Gajarishi)
- Project: [AI Calendar Planner](https://github.com/Sanika-Gajarishi/AI-Calender-Planner)

---

## 📄 License

No license file is currently present in the repository. If you plan to allow others to reuse, modify, or distribute this project, add an explicit license and make sure it matches your intentions.
