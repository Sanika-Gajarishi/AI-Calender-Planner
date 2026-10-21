# 📅 AI Calendar Planner

An AI-powered task and calendar planning application that turns natural-language task descriptions into structured tasks, then helps organize those tasks into a practical multi-day schedule. It combines a **Streamlit user interface**, a **FastAPI backend**, **PostgreSQL** persistence, **Google Gemini** for language understanding and agent-style interaction, and **Google Calendar** integration for checking busy periods and syncing scheduled blocks.

> **Project status:** This README describes the code and integrations currently present in the repository. Google OAuth credentials, a Gemini API key, PostgreSQL, and a correctly configured local environment are required for the corresponding features. 



## Table of Contents

- [Overview](#overview)
- [The Problem It Solves](#the-problem-it-solves)
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Installation and Setup](#installation-and-setup)
- [Environment Variables](#environment-variables)
- [Google Calendar Configuration](#google-calendar-configuration)
- [Database Setup and Migrations](#database-setup-and-migrations)
- [Running the Application](#running-the-application)
- [Using the Application](#using-the-application)
- [API Overview](#api-overview)
- [Testing](#testing)
- [Security Notes](#security-notes)
- [Troubleshooting](#troubleshooting)
- [Possible Future Improvements](#possible-future-improvements)
- [Author](#author)



## Overview

AI Calendar Planner is designed to make task planning more intentional and less manual. A user can enter tasks normally, or describe a task in natural language and let the AI extract fields such as title, priority, deadline, estimated duration, category, and preferred time. Tasks are stored against the user's account in a relational database.

The scheduling engine uses task information and saved work preferences to allocate tasks across a requested date range. The project also contains integration code for Google Calendar, allowing the application to retrieve calendar events, account for busy periods, and synchronize generated schedule blocks. An AI calendar assistant can answer task and scheduling questions and use application tools to perform supported actions. Rescheduling is designed around proposals that a user can approve or reject rather than silently moving a task.

The application is divided into two main components:

1. **Backend (`backend/`)** — a FastAPI service containing the API routes, business services, AI integrations, scheduling logic, authentication, database models, and Google Calendar integration.
2. **Frontend (`frontend/`)** — a Streamlit interface for registration and login, viewing and maintaining tasks, creating tasks with AI, generating schedules, and interacting with the calendar agent.



## The Problem It Solves

Managing a busy calendar usually involves several disconnected activities: writing down tasks, estimating how long each task will take, deciding what matters most, finding free time, and keeping the plan aligned with real meetings. This application brings those activities into one workflow.

Instead of needing to manually convert every task description into several fields, a user can describe the work in everyday language. The AI task service attempts to interpret that description and turn it into structured data. The scheduling engine can then work with those fields to plan tasks around the user's work preferences and calendar availability.

The objective is to support planning decisions—not to assume the AI is always correct. Users should review AI-created task details and generated schedules before relying on them.


## Key Features


### 1. Account registration and login

The backend exposes registration and login endpoints. Login returns an access token, and the Streamlit client sends that token as a Bearer token when calling protected endpoints. Task queries are scoped to the authenticated user in the task routes.

### 2. Natural-language task creation

The **Create Task with AI** flow accepts a plain-language description. The backend sends it to the task-understanding service, which uses Gemini to infer task fields. The resulting structured task includes fields such as:

- Task title and description
- Priority
- Deadline, when specified or inferred
- Estimated duration in minutes
- Category
- Preferred time

The backend then saves the task so it can be viewed and scheduled like a manually created task. AI extraction depends on the clarity of the input and the availability of the configured Gemini service; verify the result after creation.


### 3. Task management

The task API supports creating, listing, retrieving, updating, and deleting tasks. Tasks can track information used by the scheduler, including priority, deadline, estimate, category, preferred time, and status. The task list and dashboard provide a central place to review work.

When deleting a task, the current backend also attempts to delete associated Google Calendar events for scheduled blocks that have a stored Google event ID. If an event was already removed or Google Calendar returns an error, the backend logs the issue and continues the task deletion.


### 4. Smart multi-day scheduling

The scheduling implementation is separated into dedicated modules for scheduling, allocation, prioritization, finding time slots, validation, and break handling. The schedule service loads a user's saved preferences and outstanding tasks, then invokes the multi-day scheduler to arrange work over a selected date range.

The scheduling workflow is designed to consider information such as:

- Working-day start and end times
- User time zone
- Task duration and remaining work
- Task priority and deadline
- Preferred time and task attributes
- Existing schedule blocks
- Google Calendar busy periods, where the integration is configured and available

The generated schedule is saved as scheduled blocks and can be retrieved for later viewing. The exact result depends on task data, preferences, calendar availability, and the scheduler's allocation rules.


### 5. Calendar preferences

Preference models and schemas represent schedule settings including work start/end times, preferred work period, maximum daily hours, break duration, preferred task length, and time zone. These preferences give the scheduler constraints and defaults to use while producing a plan.

### 6. Google Calendar connection and event retrieval

The backend includes Google OAuth authorization and a Google Calendar service integration. The calendar endpoints can report connection status, start the OAuth connection flow, and retrieve events over a requested number of days. Calendar credentials are read from local OAuth files as described in [Google Calendar Configuration](#google-calendar-configuration).

This integration requires the user to configure a Google Cloud project and grant the requested Calendar scope. Google Calendar support will not work until the OAuth setup is complete.

### 7. Schedule synchronization

The client includes an action to synchronize a generated schedule with Google Calendar. Scheduled blocks can retain Google Calendar event IDs so later operations can reference the corresponding remote event. A successful API request should be checked for its response and the resulting events in Google Calendar; availability of this feature depends on valid OAuth credentials and Calendar API access.

### 8. AI Calendar Agent

The **AI Calendar Agent** combines a Gemini-backed chat model with application tools for supported task and calendar operations. Its agent instructions emphasize checking actual calendar information for conflict questions and avoiding unsupported claims that an event has been created or moved.

The codebase includes tools and service logic for operations such as getting pending tasks, inspecting scheduled blocks, checking availability/conflicts, generating or syncing a schedule, and proposing a reschedule. The rescheduling API includes proposal creation, approval, and rejection endpoints. A proposal is a pending change until it is explicitly approved; the agent should not describe a task as moved merely because a proposal exists.

### 9. Rescheduling proposals

The backend exposes endpoints to create a rescheduling proposal and to approve or reject it. Proposal validation handles cases such as missing records and scheduling conflicts. This approval step is intended to keep the user in control of changes to a plan.

### 10. Dashboard and calendar-oriented UI

The Streamlit frontend provides these views:

- **Dashboard** — task counts, task status, planned time, shortcuts, and Google Calendar status.
- **Create Task with AI** — describe work in natural language and create a structured task.
- **My Tasks** — review and manage tasks.
- **Smart Schedule** — generate and view planned time blocks.
- **AI Calendar Agent** — chat with the AI assistant about supported task and calendar workflows.

## How It Works

A typical workflow looks like this:

1. **Register or log in.** The frontend calls the FastAPI authentication routes and stores the returned access token in Streamlit session state.
2. **Create tasks.** Add a task manually or submit a natural-language description to the AI task endpoint. The AI service turns the description into structured fields and the backend saves the task.
3. **Configure preferences.** Provide working hours, time zone, and other scheduling preferences supported by the application.
4. **Connect Google Calendar.** Complete Google's OAuth authorization so the integration can read calendar events and, when supported, create or update events.
5. **Generate a schedule.** Select a starting date and planning horizon. The schedule service collects the user's eligible tasks and preferences, checks existing schedule data and calendar availability through its services, and calls the scheduling engine.
6. **Review the result.** View the saved schedule in the frontend and verify that task placements fit your real commitments.
7. **Use the AI agent.** Ask questions about tasks or calendar availability, or request supported actions. For rescheduling, review the proposal before approving it.
8. **Synchronize and revisit.** Where configured, synchronize generated schedule blocks with Google Calendar and return to the application as task status changes.


### High-level architecture

```text
┌──────────────────────────────┐
│       Streamlit Frontend      │
│ Dashboard / Tasks / Schedule │
│       AI Agent Chat          │
└──────────────┬───────────────┘
               │ HTTP + JSON
               │ Bearer access token
┌──────────────▼───────────────┐
│          FastAPI API          │
│ Auth, Tasks, AI, Preferences  │
│ Schedule, Agent, Calendar     │
└───────┬───────────┬──────────┘
        │           │
        │           ├─────────────────────────┐
        │           │                         │
┌───────▼────────┐ ┌▼─────────────────┐ ┌─────▼─────────────┐
│   PostgreSQL   │ │ Gemini / LangChain│ │ Google Calendar   │
│ Users, Tasks,  │ │ Task understanding│ │ OAuth + Events    │
│ Preferences,   │ │ Agent + tools     │ │ Busy-time/Sync    │
│ Schedule Blocks│ └───────────────────┘ └───────────────────┘
└────────────────┘
```

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Python, Streamlit | Interactive web interface and session-driven navigation |
| Backend API | Python, FastAPI, Uvicorn | REST endpoints and request/response validation |
| Data validation | Pydantic / Pydantic Settings | Request schemas and environment-based configuration |
| Database | PostgreSQL | Persistent users, tasks, preferences, schedule blocks, and rescheduling data |
| ORM | SQLAlchemy | Database models, queries, and sessions |
| Schema migrations | Alembic | Versioned database schema changes |
| Generative AI | Google Gemini (`gemini-2.5-flash`) | Natural-language task interpretation and agent responses |
| Agent framework | LangChain and `langchain-google-genai` | Connects the chat model to application tools |
| Calendar integration | Google Calendar API, Google Auth libraries | OAuth, event retrieval, and schedule synchronization |
| Authentication | Bearer access tokens, password hashing utilities | Account login and protected API requests |
| Testing | Pytest | Backend tests for task, scheduling, database, AI, and Calendar functionality |

Exact dependency versions are listed in `backend/requirements.txt`. The frontend currently has a `frontend/requirements.txt` file, but it contains the same broad dependency list as the backend rather than a minimal UI-only set.


## Architecture

### Frontend

`frontend/app.py` configures the Streamlit page, manages login state and navigation, and dispatches to UI components. The `APIClient` class centralizes HTTP calls so UI components do not need to construct every endpoint request themselves. It adds the access token to protected requests using the `Authorization: Bearer ...` header.


### API layer

The routers under `backend/app/api/` expose routes for users, authentication, tasks, AI task creation, preferences, schedule generation/retrieval, calendar connection/event retrieval, and agent/rescheduling actions. The API layer validates input, gets a database session where necessary, checks the current user on protected routes, invokes a service, and converts expected failures into HTTP errors.

### Service layer

The services under `backend/app/services/` separate business operations from HTTP routes. Examples include task creation, authentication, Gemini interaction, schedule generation, calendar availability, schedule persistence, and agent orchestration. This makes it easier to test business logic and update integrations without moving all logic into route handlers.


### Scheduling engine

The `backend/app/scheduler/` package separates scheduling concerns into specialized modules. The multi-day scheduling path uses task and availability representations and allocation helpers rather than relying on the language model alone to place every task. This is important because schedule placement must respect time ranges and avoid overlapping allocations. 


### Persistence and migrations

SQLAlchemy models represent application data, and Alembic holds versioned migrations under `backend/alembic/versions/`. The database URL is supplied through `DATABASE_URL`. Ensure the target database exists and migrations match the model version before launching the app.


### AI and external integrations

`GeminiService` calls Google's GenAI SDK using the configured `GEMINI_API_KEY`. The calendar agent uses a Gemini-backed LangChain chat model and registered tools. Google Calendar authorization uses a local OAuth client-secret file and stores the resulting user token in `backend/token.json` (the token is sensitive and must not be committed).


## Repository Structure

The following is a high-level guide to the current repository layout; supporting files and individual modules are omitted for readability.

```text
AI-Calender-Planner/
├── backend/
│   ├── app/
│   │   ├── agents/             # Calendar agent and agent tools
│   │   ├── api/                # FastAPI routers and dependencies
│   │   ├── core/               # Configuration, security, timezone utilities
│   │   ├── database/           # SQLAlchemy Base and connection/session setup
│   │   ├── integrations/       # Google OAuth and Google Calendar integration
│   │   ├── models/             # ORM models
│   │   ├── scheduler/          # Allocation, multi-day scheduler, priorities, slots
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── services/            # Business logic and AI/Calendar services
│   │   ├── tools/               # Calendar, schedule, and task tools
│   │   └── main.py              # FastAPI app and router registration
│   ├── alembic/
│   │   └── versions/            # Database migration scripts
│   ├── alembic.ini
│   ├── requirements.txt
│   └── tests/                   # Pytest test modules
├── frontend/
│   ├── components/
│   │   ├── agent_chat.py        # AI assistant interface
│   │   ├── calendar_view.py     # Schedule view
│   │   ├── sidebar.py           # Sidebar component
│   │   ├── task_form.py         # Task creation UI
│   │   └── task_list.py         # Task listing UI
│   ├── api_client.py            # HTTP client for the backend
│   ├── app.py                   # Streamlit entry point
│   ├── config.py                # Backend base URL
│   └── requirements.txt
├── .gitignore
└── README.md
```

## Prerequisites

Install or prepare the following before running the project:

- **Python:** use Python 3.11 or another version compatible with all pinned dependencies in `backend/requirements.txt`.
- **PostgreSQL:** a running PostgreSQL service and a database created for this application.
- **Gemini API key:** required for natural-language task creation and Gemini-backed agent features.
- **Google Cloud project:** required if you want to connect Google Calendar. Enable the Google Calendar API and configure an OAuth client.
- **Git:** to clone the repository.

Because dependencies are pinned and include recent package versions, if `pip install` fails on your Python version, verify compatibility for the specific failing package rather than upgrading every package indiscriminately.


## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Sanika-Gajarishi/AI-Calender-Planner.git
cd AI-Calender-Planner
```

### 2. Create the PostgreSQL database

Open PostgreSQL using `psql`, pgAdmin, or another PostgreSQL client and create a database. For example:

```sql
CREATE DATABASE ai_calendar_planner;
```

Use the exact database name you place in `DATABASE_URL` below. This command creates the database only; it does not configure the database user or password.



### 3. Configure the backend environment

Move to the backend directory and create a virtual environment:

**Windows PowerShell**

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks environment activation, you may use the Command Prompt activation script (`.venv\Scripts\activate.bat`) or adjust your local execution policy according to your organization's guidance.



**macOS / Linux**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create a file named `backend/.env` and add your own local values:

```dotenv
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/ai_calendar_planner
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

Replace `YOUR_PASSWORD` and `YOUR_GEMINI_API_KEY` with your own values. If your PostgreSQL installation uses a different host, port, username, or database name, update the URL accordingly. Do not wrap values in angle brackets and do not commit the `.env` file.


### 4. Initialize the database schema

The repository includes Alembic migration scripts. With the backend virtual environment active and while your shell is in the `backend/` directory, run:

```bash
alembic upgrade head
```

If the database is newly created, this applies the repository's migrations to the target database. If the command fails, verify `DATABASE_URL`, confirm that PostgreSQL is running and the database exists, and check the Alembic error before trying alternative migration commands.

The current FastAPI startup code also calls `Base.metadata.create_all()` and includes a few conditional column checks. Migrations should still be treated as the primary versioned schema-management mechanism; avoid casually mixing manual schema edits with Alembic history.


### 5. Configure Google Calendar (optional but needed for calendar features)

If you want to use Google Calendar integration, follow the [Google Calendar Configuration](#google-calendar-configuration) section before testing connection or scheduling features that require real calendar availability.


### 6. Start the backend

From the `backend/` directory, with the virtual environment active:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The local API base URL is `http://127.0.0.1:8000`. The backend defines a root route and a health route. Open the interactive API documentation at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

Keep this terminal running while using the frontend.


### 7. Start the Streamlit frontend

Open a **second terminal**. From the repository root:

**Windows PowerShell**

```powershell
cd frontend
..\backend\.venv\Scripts\Activate.ps1
streamlit run app.py
```

**macOS / Linux**

```bash
cd frontend
source ../backend/.venv/bin/activate
streamlit run app.py
```

The frontend configuration in `frontend/config.py` currently sets the API URL to `http://127.0.0.1:8000`. If the backend is running elsewhere, update `API_BASE_URL` to the correct backend URL.

Streamlit normally prints a local address (often `http://localhost:8501`) in the terminal and opens it in your browser. Register an account or log in to begin.



## Environment Variables

| Variable / file | Required? | Description |
|---|---|---|
| `DATABASE_URL` | Yes | SQLAlchemy connection URL for PostgreSQL. |
| `GEMINI_API_KEY` | Yes for AI features | API key used by the Google GenAI SDK and Gemini-backed agent. |
| `backend/credentials/google_client_secret.json` | For Google OAuth | OAuth client-secret JSON downloaded from Google Cloud. |
| `backend/token.json` | Created during OAuth | User authorization token; private local credential data. Do not commit it. |
| `frontend/config.py` → `API_BASE_URL` | Yes | URL that the Streamlit frontend uses to call FastAPI. |

The backend settings load environment values from `.env` relative to the process's working directory. Start the backend from `backend/` so `backend/.env` is discovered as expected.


## Google Calendar Configuration

Google Calendar integration uses OAuth credentials, not merely a generic Calendar API key.

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select a project.
3. Enable the **Google Calendar API** for that project.
4. Configure the OAuth consent screen and provide the required application details.
5. Create an OAuth client suitable for a **Desktop app** because the current integration uses Google's local-server OAuth flow.
6. Download the client-secret JSON file.
7. Create `backend/credentials/` and save the file as `google_client_secret.json`:

   ```text
   backend/
   └── credentials/
       └── google_client_secret.json
   ```

8. Start the backend and use **Connect Google Calendar** in the application. The first authorization may open a browser and ask you to grant Calendar access.
9. The integration writes an authorization token to `backend/token.json`. Keep this file private and out of version control.

The code requests the Calendar scope `https://www.googleapis.com/auth/calendar`. Review the scope and Google's consent requirements for your account type. Do not upload OAuth client secrets or token files to GitHub, screenshots, or public issue threads.

## Database Setup and Migrations

The application uses SQLAlchemy models and a PostgreSQL URL supplied via `DATABASE_URL`. Migration files live in `backend/alembic/versions/`.

Common Alembic commands (run from `backend/` with the virtual environment activated):

```bash
# Apply all migrations up to the current head
alembic upgrade head

# Show the current database revision
alembic current

# Show migration history
alembic history
```

Before creating a new migration, make and review the model change, then use Alembic's migration-generation workflow and inspect the generated script manually. The database should be backed up before applying schema changes to important data.

## Running the Application

Run the backend and frontend in separate terminals.

**Terminal 1 — API**

```bash
cd backend
# Activate the backend virtual environment first
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 — Streamlit UI**

```bash
cd frontend
# Activate the backend virtual environment first
streamlit run app.py
```

Then open the Streamlit URL shown in the terminal. If the interface loads but requests fail, confirm that FastAPI is reachable at the configured `API_BASE_URL` and that the backend terminal does not show configuration or database errors.

## Using the Application

### First-time setup

1. Open the Streamlit page.
2. Select **Register**, enter your name (if requested), email, and password, and submit the form.
3. Switch to **Login** and sign in with the registered account.
4. Create one or more tasks. Start with clear descriptions and realistic time estimates.
5. Configure schedule preferences using the preference flow/API supported by the current project.
6. Connect Google Calendar if you want the app to use your real calendar.
7. Open **Smart Schedule**, choose a start date and planning horizon, and generate a schedule.
8. Review the schedule, then use calendar synchronization only after confirming that the proposed blocks look correct.
9. Open **AI Calendar Agent** to ask supported questions about tasks, busy time, scheduling, or rescheduling proposals.

### Example task descriptions

Natural-language prompts you can try with **Create Task with AI** include:

- `Prepare a Python interview revision plan for 90 minutes tomorrow morning.`
- `Finish the AI Calendar Planner README by Friday; estimate 45 minutes and mark it high priority.`
- `Study SQL joins for one hour this evening.`
- `Prepare project demonstration slides for next Wednesday, around 2 hours.`

These are examples, not guaranteed interpretations. Check the generated title, deadline, duration, priority, and other fields before relying on them.

### Example AI agent questions

- `What pending tasks do I have?`
- `Show my scheduled tasks for the next week.`
- `Does my calendar have a conflict on the time I proposed?`
- `Find an available time for this task.`
- `Propose moving my scheduled task to another time.`
- `Approve rescheduling proposal 3.`

The results depend on your saved data, access token, connected Google Calendar, and the tools currently available to the agent. When the agent offers a rescheduling proposal, inspect the proposal and approve or reject its ID explicitly. 

## API Overview

The backend is a FastAPI service. Visit `/docs` while it is running to see interactive request schemas and the full endpoint definitions for the checked-out version.

| Area | Route(s) | Purpose |
|---|---|---|
| Root / health | `GET /`, `GET /health` | Basic API availability checks |
| Authentication | `POST /auth/register`, `POST /auth/login` | Register an account and obtain an access token |
| Tasks | `POST /tasks/`, `GET /tasks/`, `GET /tasks/{task_id}`, `PUT /tasks/{task_id}`, `DELETE /tasks/{task_id}` | Create and manage the current user's tasks |
| AI task creation | `POST /ai/create-task` | Convert natural-language text into a structured task |
| Schedule | `GET /schedule`, `POST /schedule/generate` | Retrieve a saved schedule or generate one for a date range |
| Calendar | `GET /calendar/status`, `POST /calendar/connect`, `GET /calendar/events` | Check connection status, authorize Google Calendar, and fetch events |
| AI agent | `POST /agent/chat` | Send a message to the calendar agent |
| Reschedule proposals | `POST /agent/reschedule-proposals`, `POST /agent/reschedule-proposals/approve`, `POST /agent/reschedule-proposals/reject` | Propose, approve, or reject a task reschedule |
| Preferences | `GET /preferences/`, `POST /preferences/` | Read or create schedule preferences in the current implementation |

Several routes require a Bearer access token. The `start_date` parameter for schedule routes uses an ISO date such as `2026-10-20`; `number_of_days` sets the number of days in the planning horizon. Exact request fields and response schemas can be inspected in Swagger UI.

### Example: checking the API health

```bash
curl http://127.0.0.1:8000/health
```

Expected response when the application starts successfully:

```json
{
  "status": "healthy"
}
```

### Example: calling an authenticated endpoint

After logging in, use the access token returned by `/auth/login`:

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://127.0.0.1:8000/tasks/
```

Replace `YOUR_ACCESS_TOKEN` with a real token. Never share a valid token publicly. 


## Testing

The backend contains a `tests/` directory with tests related to AI task creation, database setup, Gemini, Google Calendar, scheduling, and the scheduling engine. There are also standalone integration/check scripts in `backend/`.

From `backend/`, with the virtual environment active:

```bash
pytest
```

To run a specific test module:

```bash
pytest tests/test_scheduling_engine.py -v
pytest tests/test_scheduler.py -v
pytest tests/test_ai_task.py -v
```

Some tests may need environment configuration, valid external credentials, network access, and a working PostgreSQL database. A test that calls Gemini or Google Calendar can fail because of credentials, quotas, OAuth state, or network issues even when the local scheduling logic is functioning. Prefer isolated unit tests for core scheduling rules and clearly separate them from live-integration tests. 

## Security Notes

- **Never commit secrets.** Keep `backend/.env`, OAuth client secrets, token files, database passwords, and real access tokens out of Git.
- Confirm that `.gitignore` excludes local environment files and credential artifacts. If a secret has already been pushed, revoke or rotate it; deleting it from the latest commit alone may not remove it from repository history.
- Use HTTPS and proper secret management before exposing the API outside localhost.
- Review authentication expiry, password policy, and token handling before deployment.
- Limit CORS, network access, database permissions, and Google OAuth scopes to what the app needs.
- Check all AI-generated fields before scheduling. A language model can misinterpret ambiguous dates, durations, priorities, and time zones.
- Review calendar sync and rescheduling changes before applying them to a real calendar.


## Troubleshooting

### `database "ai_calendar_planner" does not exist`

Create the database in PostgreSQL or change `DATABASE_URL` so its database name matches an existing database. Confirm PostgreSQL is running and that the configured user has permission to connect.

### `DATABASE_URL` or `GEMINI_API_KEY` is missing

Check that `backend/.env` exists and contains the required values. Start Uvicorn from the `backend/` directory so settings that load `.env` can find the file. Restart the backend after changing environment values.

### Gemini request errors

Confirm that `GEMINI_API_KEY` is valid, the Gemini API is enabled/available for the key, and the account has remaining quota. The Gemini service in this repository uses `gemini-2.5-flash`. Check the backend log for the actual exception and avoid printing the key itself.

### Google OAuth client file not found

Confirm the downloaded client JSON is located at `backend/credentials/google_client_secret.json`. The code uses this path when starting OAuth authorization. Ensure the file is valid and is for the intended Google Cloud project.

### Google Calendar reports disconnected or cannot retrieve events

Run the connection flow and grant Calendar permissions. Check that the token file has not been deleted or revoked and that the Google Calendar API is enabled. Reauthorize if necessary. Treat `token.json` as a credential and do not post its contents in a support request.

### Streamlit opens but API calls fail

Confirm FastAPI is running on port `8000`, open `http://127.0.0.1:8000/health`, and verify that `frontend/config.py` points to the correct backend URL. Inspect the frontend and backend terminal errors.

### Schedule generation reports missing preferences

Schedule generation requires a preference record for the user. Add preferences through the currently supported preferences flow/API, and verify the associated user ID. The current preference routes use user ID `1` directly, so this area may need correction for user-specific behavior.

### Migration fails

Make sure you are in `backend/`, your virtual environment is active, `DATABASE_URL` points to the right database, and the PostgreSQL database already exists. Review `alembic current` and `alembic history` before attempting to stamp or manually change the revision; do not use `stamp head` as a generic fix for migration errors.

## Possible Future Improvements

Potential next steps for the project include:

- Make preference endpoints consistently use the authenticated user instead of a hard-coded ID.
- Separate frontend and backend dependency files so each environment installs only the packages it needs.
- Add a documented, validated configuration system for the frontend API URL.
- Add automated tests for authentication, multi-user data isolation, schedule conflicts, and proposal approval/rejection.
- Distinguish unit tests from tests requiring live Gemini or Google Calendar credentials.
- Improve structured logging and return consistent error messages for external integration failures.
- Add deployment instructions and production configuration after a deployable environment is selected.
- Add screenshots or a short demo GIF to illustrate the dashboard, AI task creation, schedule view, and agent chat.

These are suggestions for future work, not claims that those changes are already implemented. 


## Author

**Sanika Gajarishi**

- GitHub: [Sanika-Gajarishi](https://github.com/Sanika-Gajarishi)
- Project repository: [AI-Calender-Planner](https://github.com/Sanika-Gajarishi/AI-Calender-Planner)



If you find an issue or want to suggest an improvement, open an issue in the repository with reproducible steps and remove all passwords, tokens, and private calendar information before sharing logs.
