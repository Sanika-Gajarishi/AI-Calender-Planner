import streamlit as st


def render_sidebar():

    with st.sidebar:

        st.title("AI Calendar Planner")

        st.caption(
            "Intelligent task scheduling assistant"
        )

        st.divider()

        page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "Create Task with AI",
                "My Tasks",
                "Smart Schedule",
            ],
        )

        st.divider()

        st.caption("AI Calendar Planner")

        return page