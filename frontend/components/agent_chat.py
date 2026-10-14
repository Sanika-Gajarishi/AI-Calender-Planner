import re
from datetime import datetime

import pandas as pd
import requests
import streamlit as st


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
        st.session_state.agent_messages.append(
            {"role": "user", "content": prompt}
        )

        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            # Detect an explicit approval request with a proposal ID.
            approval_match = re.search(
                r"\bapprove\s+(?:rescheduling\s+)?proposal\s*#?\s*(\d+)\b",
                prompt,
                re.IGNORECASE,
            )

            if approval_match:
                proposal_id = int(approval_match.group(1))

                with st.spinner(
                    f"Approving proposal {proposal_id}..."
                ):
                    try:
                        result = client.approve_reschedule_proposal(
                            proposal_id
                        )

                        if (
                            result.get("success") is True
                            and result.get("status") == "approved"
                        ):
                            start = datetime.fromisoformat(
                                result["start"].replace("Z", "+00:00")
                            )
                            end = datetime.fromisoformat(
                                result["end"].replace("Z", "+00:00")
                            )

                            response = (
                                f"✅ **Proposal {proposal_id} approved "
                                f"successfully!**\n\n"
                                f"**Task:** {result.get('title', 'Scheduled task')}\n\n"
                                f"**New date:** {start.strftime('%d %B %Y')}\n\n"
                                f"**New time:** "
                                f"{start.strftime('%I:%M %p').lstrip('0')} – "
                                f"{end.strftime('%I:%M %p').lstrip('0')} IST\n\n"
                                f"**Duration:** "
                                f"{result.get('duration_minutes', 0)} minutes"
                            )

                            st.success(
                                f"Proposal {proposal_id} approved."
                            )
                            st.markdown(response)

                            # Clear cached schedule so it can be refreshed.
                            st.session_state.schedule = None

                        else:
                            response = (
                                f"The approval endpoint did not confirm "
                                f"that proposal {proposal_id} was approved. "
                                f"Response: {result}"
                            )
                            st.warning(response)

                        st.session_state.agent_messages.append(
                            {
                                "role": "assistant",
                                "content": response,
                            }
                        )

                    except requests.exceptions.HTTPError as error:
                        status_code = (
                            error.response.status_code
                            if error.response is not None
                            else None
                        )

                        try:
                            detail = error.response.json().get(
                                "detail", str(error)
                            )
                        except Exception:
                            detail = str(error)

                        if status_code == 409:
                            response = (
                                f"⚠️ Proposal {proposal_id} was not "
                                f"approved by this request because it has "
                                f"already been processed or conflicts "
                                f"with the current schedule. API detail: "
                                f"{detail}"
                            )
                        else:
                            response = (
                                f"❌ Unable to approve proposal "
                                f"{proposal_id}. API detail: {detail}"
                            )

                        st.error(response)
                        st.session_state.agent_messages.append(
                            {
                                "role": "assistant",
                                "content": response,
                            }
                        )

                    except Exception as error:
                        response = (
                            f"❌ Unable to approve proposal "
                            f"{proposal_id}: {error}"
                        )
                        st.error(response)
                        st.session_state.agent_messages.append(
                            {
                                "role": "assistant",
                                "content": response,
                            }
                        )

            else:
                # Normal messages continue to use the AI agent.
                with st.spinner("AI Calendar Agent is thinking..."):
                    try:
                        result = client.chat_with_agent(prompt)

                        response = result.get(
                            "message",
                            "I could not generate a response.",
                        )
                        tasks = result.get("tasks")

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
                        else:
                            st.markdown(response)
                            st.session_state.agent_messages.append(
                                {
                                    "role": "assistant",
                                    "content": response,
                                }
                            )

                    except Exception as error:
                        st.error(f"Agent request failed: {error}")
                        st.session_state.agent_messages.append(
                            {
                                "role": "assistant",
                                "content": f"Agent request failed: {error}",
                            }
                        )
