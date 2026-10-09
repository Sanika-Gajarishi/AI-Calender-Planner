`# 📅 AI Calendar Planner

An AI-powered productivity application that turns natural-language requests into structured tasks and builds a schedule around priorities, deadlines, preferred working times, and existing Google Calendar events.

---

### ✨ Features

- 🤖 **AI task creation** — extract task details from natural-language input using Gemini.
- 📋 **Task management** — create, update, organize, and track tasks.
- 🧠 **Intelligent scheduling** — prioritize tasks and allocate available time across multiple days.
- 📅 **Google Calendar integration** — read events, identify busy periods, and sync generated schedules.
- 🔐 **Authentication** — registration, login, JWT-based access, and user-specific data.
- ⚙️ **Personalized preferences** — configure working hours, timezone, daily scheduling limits, and break duration.
- 💬 **AI Calendar Agent** — interact with the planner through an agent-style chat interface.

---

### 🧰 Technology Stack

- **Backend:** Python, FastAPI
- **Frontend:** Streamlit
- **AI:** Google Gemini API
- **Database:** SQLAlchemy, configured through `DATABASE_URL`
- **Migrations:** Alembic
- **Calendar:** Google Calendar API, Google OAuth
- **Authentication:** JWT, password hashing
- **Testing:** Pytest

---

### 🏗️ Project Structure

```bash
AI-Calender-Planner/
├── backend/
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Request and response schemas
│   │   ├── scheduler/      # Scheduling logic
│   │   ├── services/       # AI, tasks, and schedule services
│   │   └── integrations/   # Google Calendar and OAuth
│   ├── alembic/            # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── components/
│   ├── app.py
│   └── api_client.py
└── README.md
```

---

### ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/Sanika-Gajarishi/AI-Calender-Planner.git
cd AI-Calender-Planner
```

Create and activate a virtual environment:

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

---

### 🔑 Environment Configuration

Create a `.env` file in the `backend/` directory with the configuration required by the backend.

```bash
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=your_database_connection_url
```

The application also requires Google Calendar OAuth credentials for calendar features. Follow Google's OAuth setup instructions and keep credential files and tokens private. Never commit API keys, OAuth client secrets, or access tokens.

---

### ▶️ Run the Application

Start the FastAPI backend from the `backend/` directory:

```bash
cd backend
uvicorn app.main:app --reload
```

In a separate terminal, activate the same virtual environment and start the Streamlit frontend:

```bash
cd frontend
streamlit run app.py
```

The backend API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

### 🧠 Scheduling Workflow

```text
Natural-language task
        ↓
Gemini extracts task details
        ↓
Tasks saved to the database
        ↓
Read user preferences and calendar events
        ↓
Prioritize tasks and find free time slots
        ↓
Generate multi-day schedule
        ↓
Sync scheduled blocks to Google Calendar
```

---

### 👩‍💻 Author

**Sanika Gajarishi**  
GitHub: https://github.com/Sanika-Gajarishi

---


### 📄 License

No license file is currently specified in the repository. Add a license file if you intend to publish the project for reuse.
