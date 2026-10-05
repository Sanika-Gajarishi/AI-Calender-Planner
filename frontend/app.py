import streamlit as st

from api_client import APIClient
from components.calendar_view import render_calendar_view
from components.task_form import render_task_form
from components.task_list import render_task_list


st.set_page_config(
    page_title="AI Calendar Planner",
    page_icon="📅",
    layout="wide",
)


PAGES = (
    "Dashboard",
    "Create Task with AI",
    "My Tasks",
    "Smart Schedule",
)


def navigate_to(page):
    st.session_state.page = page


if "token" not in st.session_state:
    st.session_state.token = None

if "schedule" not in st.session_state:
    st.session_state.schedule = None

if "page" not in st.session_state:
    st.session_state.page = PAGES[0]
elif st.session_state.page not in PAGES:
    st.session_state.page = PAGES[0]


if not st.session_state.token:
    st.title("📅 AI Calendar Planner")
    st.caption("Your intelligent task scheduling assistant")
    st.subheader("Login")

    with st.form("login_form"):
        email = st.text_input(
            "Email",
            placeholder="Enter your email",
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
        )
        submitted = st.form_submit_button(
            "Login",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not email.strip() or not password:
            st.warning("Please enter your email and password.")
        else:
            try:
                result = APIClient().login(email.strip(), password)
                st.session_state.token = result["access_token"]
                st.session_state.schedule = None
                st.success("Login successful.")
                st.rerun()
            except Exception as error:
                st.error(f"Login failed: {error}")

else:
    client = APIClient(token=st.session_state.token)

    with st.sidebar:
        st.success("Logged in")
        page = st.radio(
            "Navigation",
            PAGES,
            key="page",
        )

        if st.button("Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.schedule = None
            st.session_state.page = PAGES[0]
            st.rerun()

    if page == "Dashboard":
        st.header("👋 Welcome to your AI Calendar")
        st.write(
            "Create tasks with AI and organize them into a schedule."
        )

        try:
            tasks = client.get_tasks()
        except Exception as error:
            st.error(f"Unable to load dashboard tasks: {error}")
            tasks = None

        pending_tasks = (
            sum(
                1
                for task in tasks
                if task.get("status") != "completed"
            )
            if tasks is not None
            else "—"
        )
        completed_tasks = (
            sum(
                1
                for task in tasks
                if task.get("status") == "completed"
            )
            if tasks is not None
            else "—"
        )
        planned_minutes = (
            sum(
                task.get("estimated_minutes", 0)
                for task in tasks
            )
            if tasks is not None
            else None
        )

        metric_columns = st.columns(4)
        metric_columns[0].metric(
            "Total Tasks",
            len(tasks) if tasks is not None else "—",
        )
        metric_columns[1].metric("Pending", pending_tasks)
        metric_columns[2].metric("Completed", completed_tasks)
        metric_columns[3].metric(
            "Planned Time",
            (
                f"{planned_minutes // 60}h "
                f"{planned_minutes % 60}m"
                if planned_minutes is not None
                else "—"
            ),
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🤖 AI Task Creation")
            st.write(
                "Describe a task naturally and let AI extract its details."
            )
            if st.button(
                "Create AI Task",
                use_container_width=True,
            ):
                navigate_to("Create Task with AI")
                st.rerun()

        with col2:
            st.subheader("📅 Smart Scheduling")
            st.write(
                "Generate an optimized schedule while "
                "respecting your working hours and "
                "Google Calendar busy periods."
            )
            if st.button(
                "📅 Generate Schedule",
                use_container_width=True,
            ):
                navigate_to("Smart Schedule")
                st.rerun()

        st.divider()
        st.subheader("📋 Recent Tasks")
        if tasks is not None:
            if tasks:
                for task in tasks[:5]:
                    status = task.get(
                        "status",
                        "pending",
                    )
                    st.write(
                        f"**{task.get('title', 'Untitled')}** "
                        f"— {status.title()}"
                    )
            else:
                st.info(
                    "No tasks yet. Create your first task "
                    "using AI."
                )

    elif page == "Create Task with AI":
        render_task_form(client)

    elif page == "My Tasks":
        render_task_list(client)

    elif page == "Smart Schedule":
        render_calendar_view(client)
