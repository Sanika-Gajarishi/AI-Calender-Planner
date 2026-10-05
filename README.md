# 📅 AI Calendar Planner

An intelligent AI-powered calendar and task scheduling application that converts natural-language tasks into structured tasks and automatically creates an optimized schedule around user preferences and existing Google Calendar events.

The application combines **Generative AI, task management, calendar integration, and intelligent scheduling** into one productivity platform.

---

## 🚀 Features

### 🔐 User Authentication
- User registration and login
- JWT-based authentication
- Password hashing and secure authentication
- User-specific tasks and preferences

### 🤖 AI Task Creation
Create tasks using natural language instead of manually filling forms.

Example:

> "I need to prepare for a Python interview for 2 hours every evening until October 9."

The AI extracts structured information such as:

- Task title
- Description
- Priority
- Category
- Estimated duration
- Preferred time
- Deadline

---

### 📋 Task Management

Users can:

- Create tasks
- View tasks
- Update tasks
- Delete tasks
- Track task status
- Set priorities
- Define estimated task duration
- Add deadlines and preferred working times

---

### 🧠 Intelligent Scheduling

The scheduling engine automatically creates a schedule based on:

- Task priority
- Estimated duration
- Deadlines
- Preferred time
- User availability
- Existing calendar events
- Working hours
- Multiple-day scheduling

The system can split tasks across multiple available time slots when required.

---

### 📅 Google Calendar Integration

The application integrates with Google Calendar to:

- Read existing calendar events
- Detect busy periods
- Avoid scheduling conflicts
- Create generated schedule events
- Identify events created by AI Calendar Planner
- Prevent duplicate scheduled events

Example workflow:

```text
Google Calendar
      ↓
Fetch existing events
      ↓
Convert events into busy time slots
      ↓
Scheduling Engine
      ↓
Find available time
      ↓
Generate optimized schedule
      ↓
Sync schedule to Google Calendar
