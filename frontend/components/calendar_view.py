from datetime import date, datetime

import streamlit as st


def format_datetime(value):
    """Convert ISO datetime into a user-friendly date/time."""
    if not value:
        return ""

    dt = datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )

    return dt


def format_time(dt):
    """Format time as 12-hour AM/PM."""
    return dt.strftime("%I:%M %p").lstrip("0")


def format_duration(start, end):
    """Calculate and format duration."""
    minutes = int((end - start).total_seconds() / 60)

    hours = minutes // 60
    remaining_minutes = minutes % 60

    if hours and remaining_minutes:
        return f"{hours} hr {remaining_minutes} min"

    if hours:
        return f"{hours} hr"

    return f"{remaining_minutes} min"


def render_calendar_view(client):

    st.header("📅 Smart Schedule")

    st.write(
        "Generate an optimized schedule from your pending tasks."
    )

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Start date",
            value=date.today(),
        )

    with col2:
        number_of_days = st.number_input(
            "Number of days",
            min_value=1,
            max_value=30,
            value=7,
        )

    if st.button(
        "🧠 Generate Smart Schedule",
        type="primary",
        use_container_width=True,
    ):

        with st.spinner(
            "AI Calendar Planner is creating your schedule..."
        ):

            try:

                result = client.generate_schedule(
                    start_date.isoformat(),
                    number_of_days,
                )

                st.session_state.schedule = result

            except Exception as error:

                st.error(
                    f"Unable to generate schedule: {error}"
                )

    schedule = st.session_state.get("schedule")

    if not schedule:
        st.info(
            "Choose a date and generate your schedule."
        )
        return

    items = schedule.get("items", [])

    total_minutes = schedule.get(
        "total_minutes",
        0,
    )

    hours = total_minutes // 60
    minutes = total_minutes % 60

    if hours and minutes:
        total_display = f"{hours} hr {minutes} min"
    elif hours:
        total_display = f"{hours} hr"
    else:
        total_display = f"{minutes} min"

    st.success(
        f"Schedule generated successfully — "
        f"{total_display} planned."
    )

    if not items:

        st.warning(
            "No tasks could be scheduled for this period."
        )
        return

    st.subheader("📋 Your Schedule")

    for item in items:

        start = format_datetime(
            item.get("start", "")
        )

        end = format_datetime(
            item.get("end", "")
        )

        title = item.get(
            "title",
            "Untitled task",
        )

        priority = item.get(
            "priority",
            "medium",
        )

        duration = format_duration(
            start,
            end,
        )

        date_display = (
            f"{start.strftime('%A, %B')} {start.day}"
        )

        start_time = format_time(start)
        end_time = format_time(end)

        with st.container(border=True):

            col1, col2 = st.columns([5, 1])

            with col1:

                st.markdown(
                    f"### {title}"
                )

                st.write(
                    f"📅 **{date_display}**"
                )

                st.write(
                    f"🕐 **{start_time} – {end_time}**"
                )

                st.caption(
                    f"⏱️ Duration: {duration}"
                )

            with col2:

                st.write(
                    f"**{priority.upper()}**"
                )