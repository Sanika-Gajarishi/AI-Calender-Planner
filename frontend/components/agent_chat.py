import streamlit as st
import pandas as pd


def build_task_table(tasks):
    display_tasks = []

    for index, task in enumerate(tasks, start=1):

        deadline = task.get("deadline")

        if deadline:
            try:
                deadline = pd.to_datetime(deadline).strftime(
                    "%d %b %Y, %I:%M %p"
                )
            except Exception:
                pass
        else:
            deadline = "No deadline"

        display_tasks.append(
            {
                "Sr. No.": index,
                "Task": task.get("title", ""),
                "Priority": task.get("priority", "").capitalize(),
                "Duration": f"{task.get('estimated_minutes', 0)} min",
                "Deadline": deadline,
            }
        )

    return pd.DataFrame(display_tasks)


def render_agent_chat(client):

    st.header("🤖 AI Calendar Agent")

    st.write(
        "Ask the AI agent to manage your tasks, "
        "schedule, and Google Calendar."
    )

    st.divider()

    if "agent_messages" not in st.session_state:
        st.session_state.agent_messages = []

    # Display previous messages
    for message in st.session_state.agent_messages:

        with st.chat_message(message["role"]):

            if message.get("type") == "tasks":

                tasks = message.get("tasks", [])

                st.write("### Here are your pending tasks:")

                if tasks:
                    df = build_task_table(tasks)

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info(
                        "You currently have no pending tasks."
                    )

            else:
                st.write(message["content"])

    prompt = st.chat_input(
        "Ask your AI Calendar Agent..."
    )

    if prompt:

        # Display user message
        st.session_state.agent_messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        with st.chat_message("user"):
            st.write(prompt)

        # Agent response
        with st.chat_message("assistant"):

            with st.spinner(
                "AI Calendar Agent is thinking..."
            ):

                try:

                    result = client.chat_with_agent(prompt)

                    response = result.get(
                        "message",
                        "I could not generate a response.",
                    )

                    tasks = result.get("tasks")

                    # TASK RESPONSE
                    if tasks is not None:

                        st.write("Here are your pending tasks:")

                        if tasks:

                            df = build_task_table(tasks)

                            st.dataframe(
                                df,
                                use_container_width=True,
                                hide_index=True,
                            )

                        else:

                            st.info(
                                "You currently have no pending tasks."
                            )

                        st.session_state.agent_messages.append(
                            {
                                "role": "assistant",
                                "content": response,
                                "type": "tasks",
                                "tasks": tasks,
                            }
                        )

                    # NORMAL AGENT RESPONSE
                    else:

                        st.write(response)

                        st.session_state.agent_messages.append(
                            {
                                "role": "assistant",
                                "content": response,
                            }
                        )

                except Exception as error:

                    st.error(
                        f"Agent request failed: {error}"
                    )