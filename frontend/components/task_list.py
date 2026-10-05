import streamlit as st


def render_task_list(client):

    st.header("📋 My Tasks")

    try:

        tasks = client.get_tasks()

    except Exception as error:

        st.error(
            f"Unable to load tasks: {error}"
        )

        return

    if not tasks:

        st.info(
            "You don't have any tasks yet. "
            "Create your first task using AI."
        )

        return

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    pending = sum(
        1
        for task in tasks
        if task.get("status") != "completed"
    )

    completed = sum(
        1
        for task in tasks
        if task.get("status") == "completed"
    )

    total_minutes = sum(
        task.get("estimated_minutes", 0)
        for task in tasks
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Tasks",
            len(tasks),
        )

    with col2:
        st.metric(
            "Pending",
            pending,
        )

    with col3:
        st.metric(
            "Planned Time",
            f"{total_minutes // 60}h "
            f"{total_minutes % 60}m",
        )

    st.divider()

    # --------------------------------------------------
    # Task list
    # --------------------------------------------------

    for task in tasks:

        task_id = task["id"]

        title = task.get(
            "title",
            "Untitled task",
        )

        description = task.get(
            "description",
        )

        priority = task.get(
            "priority",
            "medium",
        )

        category = task.get(
            "category",
            "General",
        )

        duration = task.get(
            "estimated_minutes",
            0,
        )

        status = task.get(
            "status",
            "pending",
        )

        deadline = task.get(
            "deadline",
        )

        with st.container(
            border=True
        ):

            col1, col2, col3 = st.columns(
                [5, 2, 1]
            )

            with col1:

                st.subheader(
                    title
                )

                if description:

                    st.write(
                        description
                    )

                st.caption(
                    f"Priority: {priority.title()} "
                    f"| Category: {category} "
                    f"| Duration: {duration} min"
                )

                if deadline:

                    st.caption(
                        f"⏰ Deadline: {deadline}"
                    )

            with col2:

                if status == "completed":

                    st.success(
                        "Completed"
                    )

                else:

                    st.info(
                        status.title()
                    )

            with col3:

                if st.button(
                    "🗑️",
                    key=f"delete_{task_id}",
                    help="Delete task",
                ):

                    try:

                        client.delete_task(
                            task_id
                        )

                        st.success(
                            "Task deleted."
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            str(error)
                        )