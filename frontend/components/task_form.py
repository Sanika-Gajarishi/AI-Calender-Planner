import streamlit as st


def render_task_form(client):

    st.header("🤖 Create Task with AI")

    st.write(
        "Describe what you need to do in natural language. "
        "AI will extract the task details automatically."
    )

    st.divider()

    text = st.text_area(
        "Describe your task",
        placeholder=(
            "Example: I need to prepare for a Python interview "
            "for 2 hours every evening until October 9."
        ),
        height=150,
    )

    if st.button(
        "✨ Create Task with AI",
        type="primary",
        use_container_width=True,
    ):

        if not text.strip():
            st.warning("Please describe your task.")
            return

        with st.spinner("AI is understanding your task..."):

            try:
                result = client.create_ai_task(
                    text.strip()
                )

                st.success(
                    result.get(
                        "message",
                        "Task created successfully!",
                    )
                )

                task = result.get("task", {})

                if task:

                    st.subheader("Task Created")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(
                            f"**Title:** {task.get('title')}"
                        )
                        st.write(
                            f"**Priority:** {task.get('priority')}"
                        )
                        st.write(
                            f"**Category:** {task.get('category')}"
                        )

                    with col2:
                        st.write(
                            f"**Duration:** "
                            f"{task.get('estimated_minutes')} minutes"
                        )
                        st.write(
                            f"**Preferred time:** "
                            f"{task.get('preferred_time')}"
                        )
                        st.write(
                            f"**Status:** {task.get('status')}"
                        )

                    st.info(
                        "Your task is now available in My Tasks "
                        "and can be included in Smart Schedule."
                    )

            except Exception as error:

                st.error(
                    f"Unable to create task: {error}"
                )