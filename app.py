import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta

from database import (
    init_db,
    add_task,
    update_task,
    delete_task,
    get_tasks,
    add_goal,
    update_goal,
    get_goals,
    add_note,
    get_notes,
    delete_note,
    add_study_plan,
    get_study_plans,
    save_preference,
    get_preference,
    get_analytics,
)

from ai_engine import (
    ai_chat,
    generate_study_plan,
    analyze_notes,
    breakdown_goal,
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="LifeOS AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# DATABASE
# =========================================================

init_db()

# =========================================================
# PREMIUM DARK UI
# =========================================================

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
    --bg: #080b12;
    --panel: #101520;
    --panel2: #151b28;
    --border: rgba(255,255,255,0.08);
    --text: #f4f7fb;
    --muted: #8993a6;
    --purple: #8b5cf6;
    --cyan: #22d3ee;
    --green: #34d399;
    --yellow: #fbbf24;
    --red: #f87171;
}

html,
body,
[class*="css"] {
    font-family: "DM Sans", sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 15% 0%,
            rgba(139,92,246,0.14),
            transparent 30%
        ),
        radial-gradient(
            circle at 85% 10%,
            rgba(34,211,238,0.08),
            transparent 25%
        ),
        var(--bg);
    color: var(--text);
}

[data-testid="stSidebar"] {
    background: #0b0f17;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

h1,
h2,
h3,
h4 {
    font-family: "Space Grotesk", sans-serif !important;
}

h1 {
    font-size: 2.3rem !important;
}

h2 {
    font-size: 1.5rem !important;
}

h3 {
    font-size: 1.1rem !important;
}

.stButton > button {
    min-height: 42px;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.08);
    background: #151b28;
    color: #ffffff;
    font-weight: 600;
}

.stButton > button:hover {
    border-color: rgba(139,92,246,0.8);
    color: white;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stDateInput input {
    background: #111722 !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
}

div[data-baseweb="select"] > div {
    background: #111722;
    border-radius: 10px;
}

div[data-testid="stMetric"] {
    background:
        linear-gradient(
            145deg,
            #111722,
            #0d121b
        );
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 18px;
}

div[data-testid="stMetricLabel"] {
    color: #8f99ab !important;
}

div[data-testid="stMetricValue"] {
    color: white !important;
}

.stProgress > div > div > div > div {
    background: linear-gradient(
        90deg,
        #8b5cf6,
        #22d3ee
    );
}

.hero {
    padding: 28px;
    border-radius: 22px;
    border: 1px solid rgba(139,92,246,0.22);
    background:
        linear-gradient(
            120deg,
            rgba(139,92,246,0.16),
            rgba(34,211,238,0.04)
        ),
        #0f141f;
    margin-bottom: 24px;
}

.hero .eyebrow {
    color: #a78bfa;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

.hero h1 {
    margin: 6px 0;
}

.hero p {
    color: #9aa5b7;
    margin: 0;
}

.card {
    background:
        linear-gradient(
            145deg,
            rgba(18,24,36,0.98),
            rgba(12,16,25,0.98)
        );
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 14px;
    box-shadow: 0 14px 35px rgba(0,0,0,0.14);
}

.small-muted {
    color: #8d97a9;
    font-size: 0.85rem;
}

.badge {
    display: inline-block;
    padding: 5px 9px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
}

.high {
    background: rgba(248,113,113,0.12);
    color: #fca5a5;
}

.medium {
    background: rgba(251,191,36,0.12);
    color: #fcd34d;
}

.low {
    background: rgba(52,211,153,0.12);
    color: #6ee7b7;
}

.section-title {
    margin-top: 28px;
    margin-bottom: 12px;
}

</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def page_header(title, subtitle):
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">LIFEOS AI</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_date(value):
    if not value:
        return "—"

    try:
        return datetime.strptime(
            str(value),
            "%Y-%m-%d"
        ).strftime("%b %d, %Y")
    except Exception:
        return str(value)


def priority_badge(priority):
    priority = str(priority).lower()

    return (
        f'<span class="badge {priority}">'
        f'{priority.title()}'
        f'</span>'
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## ✦ LifeOS AI")

    st.caption("Personal AI Command Center")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🤖 AI Assistant",
            "✅ Tasks",
            "📚 Study Planner",
            "📝 AI Notes",
            "🎯 Goals",
            "📊 Analytics",
            "⚙️ Settings",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown(
        f"""
        **Today**

        {date.today().strftime("%A, %d %B %Y")}
        """
    )

    st.caption("Your productivity data is stored locally.")

# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    display_name = get_preference(
        "display_name",
        "there"
    )

    page_header(
        f"Good to see you, {display_name} 👋",
        "Your personal overview of tasks, goals, study and productivity."
    )

    tasks = get_tasks()
    goals = get_goals()

    today = date.today().isoformat()

    today_tasks = [
        task
        for task in tasks
        if task["deadline"] == today
        and task["status"] != "completed"
    ]

    completed_tasks = [
        task
        for task in tasks
        if task["status"] == "completed"
    ]

    pending_tasks = [
        task
        for task in tasks
        if task["status"] != "completed"
    ]

    active_goals = [
        goal
        for goal in goals
        if goal["status"] != "completed"
    ]

    total_tasks = len(tasks)

    productivity = (
        round(
            len(completed_tasks)
            / total_tasks
            * 100
        )
        if total_tasks
        else 0
    )

    # -------------------------
    # METRICS
    # -------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Productivity Score",
        f"{productivity}%"
    )

    c2.metric(
        "Today's Tasks",
        len(today_tasks)
    )

    c3.metric(
        "Completed Tasks",
        len(completed_tasks)
    )

    c4.metric(
        "Active Goals",
        len(active_goals)
    )

    # -------------------------
    # MAIN CONTENT
    # -------------------------

    st.markdown(
        '<div class="section-title">Today\'s Focus</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns([1.4, 1])

    with left:

        st.markdown("### 📌 Today's Tasks")

        if today_tasks:

            for task in today_tasks[:8]:

                st.markdown(
                    f"""
                    <div class="card">

                    <b>{task["title"]}</b>

                    <br>

                    <span class="small-muted">
                    {task["category"]}
                    •
                    {format_date(task["deadline"])}
                    </span>

                    <br><br>

                    {priority_badge(task["priority"])}

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        else:

            st.info(
                "No unfinished tasks are due today. "
                "You're clear for now."
            )

    with right:

        st.markdown("### 🎯 Active Goals")

        if active_goals:

            for goal in active_goals[:6]:

                progress = max(
                    0,
                    min(
                        100,
                        int(goal["progress"])
                    )
                )

                st.markdown(
                    f"**{goal['title']}**"
                )

                st.progress(
                    progress / 100
                )

                st.caption(
                    f"{progress}% complete • "
                    f"Target: {format_date(goal['deadline'])}"
                )

        else:

            st.info(
                "You don't have any active goals yet."
            )

    # -------------------------
    # QUICK ACTIONS
    # -------------------------

    st.markdown("### ⚡ Quick Actions")

    q1, q2, q3, q4 = st.columns(4)

    if q1.button(
        "＋ Add Task",
        use_container_width=True
    ):
        st.info(
            "Open **Tasks** from the sidebar to add a task."
        )

    if q2.button(
        "🤖 Ask AI",
        use_container_width=True
    ):
        st.info(
            "Open **AI Assistant** from the sidebar."
        )

    if q3.button(
        "🎯 New Goal",
        use_container_width=True
    ):
        st.info(
            "Open **Goals** from the sidebar."
        )

    if q4.button(
        "📝 New Note",
        use_container_width=True
    ):
        st.info(
            "Open **AI Notes** from the sidebar."
        )

    # -------------------------
    # RECENT ACTIVITY
    # -------------------------

    st.markdown("### 🕘 Recent Activity")

    if tasks:

        recent_tasks = sorted(
            tasks,
            key=lambda x: x["created_at"],
            reverse=True
        )[:5]

        for task in recent_tasks:

            status = (
                "Completed"
                if task["status"] == "completed"
                else "Pending"
            )

            st.markdown(
                f"""
                <div class="card">
                    <b>{task["title"]}</b>
                    <br>
                    <span class="small-muted">
                    {task["category"]} • {status}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:

        st.info(
            "Your recent activity will appear here."
        )

# =========================================================
# AI ASSISTANT
# =========================================================

elif page == "🤖 AI Assistant":

    page_header(
        "LifeOS Assistant",
        "Your AI productivity partner for planning, studying, goals and organization."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(
                message["content"]
            )

    prompt = st.chat_input(
        "Ask LifeOS anything..."
    )

    if prompt:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            with st.spinner(
                "LifeOS is thinking..."
            ):

                history = [
                    (
                        item["role"],
                        item["content"]
                    )
                    for item in st.session_state.messages[-8:]
                ]

                response = ai_chat(
                    prompt,
                    history
                )

            if response:

                st.markdown(response)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )

# =========================================================
# TASK MANAGER
# =========================================================

elif page == "✅ Tasks":

    page_header(
        "Smart Task Manager",
        "Capture, organize and complete the work that matters."
    )

    # ADD TASK

    with st.expander(
        "＋ Add New Task",
        expanded=True
    ):

        with st.form("task_form"):

            c1, c2, c3 = st.columns(
                [2, 1, 1]
            )

            title = c1.text_input(
                "Task Title",
                placeholder="Complete Python practice"
            )

            category = c2.selectbox(
                "Category",
                [
                    "Study",
                    "Work",
                    "Personal",
                    "Projects",
                    "Other",
                ]
            )

            priority = c3.selectbox(
                "Priority",
                [
                    "High",
                    "Medium",
                    "Low",
                ]
            )

            c4, c5 = st.columns(2)

            deadline = c4.date_input(
                "Deadline",
                value=date.today()
            )

            notes = c5.text_input(
                "Notes",
                placeholder="Optional notes"
            )

            submit = st.form_submit_button(
                "＋ Add Task",
                use_container_width=True
            )

            if submit:

                if not title.strip():

                    st.error(
                        "Please enter a task title."
                    )

                else:

                    add_task(
                        title.strip(),
                        category,
                        priority,
                        deadline.isoformat(),
                        notes.strip()
                    )

                    st.success(
                        "Task added successfully."
                    )

                    st.rerun()

    # FILTERS

    tasks = get_tasks()

    st.markdown("### Your Tasks")

    if tasks:

        f1, f2, f3 = st.columns(3)

        category_filter = f1.selectbox(
            "Category",
            [
                "All",
                "Study",
                "Work",
                "Personal",
                "Projects",
                "Other",
            ]
        )

        status_filter = f2.selectbox(
            "Status",
            [
                "All",
                "Pending",
                "Completed",
            ]
        )

        sort_filter = f3.selectbox(
            "Sort By",
            [
                "Deadline",
                "Priority",
                "Newest",
            ]
        )

        filtered = tasks.copy()

        if category_filter != "All":

            filtered = [
                t
                for t in filtered
                if t["category"]
                == category_filter
            ]

        if status_filter == "Pending":

            filtered = [
                t
                for t in filtered
                if t["status"]
                != "completed"
            ]

        elif status_filter == "Completed":

            filtered = [
                t
                for t in filtered
                if t["status"]
                == "completed"
            ]

        if sort_filter == "Deadline":

            filtered.sort(
                key=lambda x:
                x["deadline"]
                or "9999-12-31"
            )

        elif sort_filter == "Priority":

            order = {
                "High": 0,
                "Medium": 1,
                "Low": 2,
            }

            filtered.sort(
                key=lambda x:
                order.get(
                    x["priority"],
                    9
                )
            )

        else:

            filtered.sort(
                key=lambda x:
                x["created_at"],
                reverse=True
            )

        # TASK LIST

        for task in filtered:

            cols = st.columns(
                [
                    0.08,
                    2.3,
                    0.8,
                    0.8,
                    0.7,
                ]
            )

            completed = cols[0].checkbox(
                "",
                value=(
                    task["status"]
                    == "completed"
                ),
                key=f"complete_{task['id']}"
            )

            if completed != (
                task["status"]
                == "completed"
            ):

                update_task(
                    task["id"],
                    status=(
                        "completed"
                        if completed
                        else "pending"
                    )
                )

                st.rerun()

            cols[1].markdown(
                f"""
                **{task["title"]}**

                <span class="small-muted">
                {task["category"]}
                •
                Deadline:
                {format_date(task["deadline"])}
                </span>
                """,
                unsafe_allow_html=True
            )

            cols[2].markdown(
                priority_badge(
                    task["priority"]
                ),
                unsafe_allow_html=True
            )

            cols[3].caption(
                task["status"].title()
            )

            if cols[4].button(
                "Delete",
                key=f"delete_{task['id']}"
            ):

                delete_task(
                    task["id"]
                )

                st.rerun()

    else:

        st.info(
            "No tasks yet. Add your first task above."
        )

# =========================================================
# STUDY PLANNER
# =========================================================

elif page == "📚 Study Planner":

    page_header(
        "AI Study Planner",
        "Turn your subjects, chapters and exam date into a realistic study roadmap."
    )

    with st.form("study_plan_form"):

        c1, c2 = st.columns(2)

        subject = c1.text_input(
            "Subject",
            placeholder="Computer Science"
        )

        exam_date = c2.date_input(
            "Exam Date",
            value=date.today()
            + timedelta(days=10)
        )

        topics = st.text_area(
            "Topics / Chapters",
            height=150,
            placeholder=(
                "Chapter 1\n"
                "Chapter 2\n"
                "Functions\n"
                "Lists\n"
                "Dictionaries"
            )
        )

        c3, c4 = st.columns(2)

        hours = c3.number_input(
            "Study Hours Per Day",
            min_value=0.5,
            max_value=12.0,
            value=2.0,
            step=0.5
        )

        difficulty = c4.selectbox(
            "Difficulty Level",
            [
                "Easy",
                "Medium",
                "Hard",
                "Very Hard",
            ]
        )

        generate = st.form_submit_button(
            "✦ Generate AI Study Plan",
            use_container_width=True
        )

    if generate:

        if (
            not subject.strip()
            or not topics.strip()
        ):

            st.error(
                "Please enter subject and topics."
            )

        else:

            with st.spinner(
                "Creating your study plan..."
            ):

                result = generate_study_plan(
                    subject,
                    topics,
                    exam_date.isoformat(),
                    hours,
                    difficulty
                )

            if result:

                add_study_plan(
                    subject,
                    exam_date.isoformat(),
                    result
                )

                st.success(
                    "Study plan generated and saved."
                )

                st.markdown(
                    "### 📚 Your AI Study Plan"
                )

                st.markdown(result)

    st.markdown("### Saved Study Plans")

    plans = get_study_plans()

    if plans:

        for plan in plans:

            with st.expander(
                f"{plan['subject']} • "
                f"Exam: {format_date(plan['exam_date'])}"
            ):

                st.markdown(
                    plan["plan"]
                )

    else:

        st.info(
            "Your saved study plans will appear here."
        )

# =========================================================
# AI NOTES
# =========================================================

elif page == "📝 AI Notes":

    page_header(
        "AI Notes",
        "Transform your notes into summaries, concepts, flashcards and quizzes."
    )

    note_title = st.text_input(
        "Note Title",
        placeholder="Python Functions"
    )

    note_body = st.text_area(
        "Your Notes",
        height=300,
        placeholder=(
            "Paste your class notes here..."
        )
    )

    if st.button(
        "✦ Analyze Notes",
        use_container_width=True
    ):

        if not note_body.strip():

            st.error(
                "Please enter some notes first."
            )

        else:

            with st.spinner(
                "Analyzing your notes..."
            ):

                result = analyze_notes(
                    note_body
                )

            if result:

                add_note(
                    note_title.strip()
                    or "Untitled Note",
                    note_body,
                    result
                )

                st.success(
                    "AI analysis completed."
                )

                st.markdown(
                    "### ✨ AI Analysis"
                )

                st.markdown(
                    result
                )

    st.markdown("### Saved Notes")

    notes = get_notes()

    if notes:

        for note in notes:

            with st.expander(
                f"{note['title']} • "
                f"{note['created_at'][:10]}"
            ):

                st.markdown(
                    note["analysis"]
                    or "No AI analysis available."
                )

                if st.button(
                    "Delete Note",
                    key=f"delete_note_{note['id']}"
                ):

                    delete_note(
                        note["id"]
                    )

                    st.rerun()

    else:

        st.info(
            "No notes saved yet."
        )

# =========================================================
# GOALS
# =========================================================

elif page == "🎯 Goals":

    page_header(
        "Goal Tracker",
        "Break big goals into milestones, weekly targets and daily actions."
    )

    with st.form("goal_form"):

        goal_title = st.text_input(
            "Your Goal",
            placeholder="Learn Python in 30 days"
        )

        target_date = st.date_input(
            "Target Date",
            value=date.today()
            + timedelta(days=30)
        )

        context = st.text_area(
            "Goal Context",
            placeholder=(
                "Why is this goal important?"
            )
        )

        create_goal = st.form_submit_button(
            "✦ Create AI Goal Roadmap",
            use_container_width=True
        )

    if create_goal:

        if not goal_title.strip():

            st.error(
                "Please enter a goal."
            )

        else:

            with st.spinner(
                "Building your goal roadmap..."
            ):

                roadmap = breakdown_goal(
                    goal_title,
                    target_date.isoformat(),
                    context
                )

            add_goal(
                goal_title.strip(),
                target_date.isoformat(),
                0,
                roadmap
            )

            st.success(
                "Goal created successfully."
            )

            st.markdown(
                "### 🎯 AI Goal Roadmap"
            )

            st.markdown(
                roadmap
            )

    st.markdown("### Your Goals")

    goals = get_goals()

    if goals:

        for goal in goals:

            st.markdown(
                f"### {goal['title']}"
            )

            st.caption(
                f"Target date: "
                f"{format_date(goal['deadline'])}"
            )

            current_progress = int(
                goal["progress"]
            )

            progress = st.slider(
                "Progress",
                0,
                100,
                current_progress,
                key=f"progress_{goal['id']}"
            )

            if progress != current_progress:

                update_goal(
                    goal["id"],
                    progress=progress,
                    status=(
                        "completed"
                        if progress == 100
                        else "active"
                    )
                )

                st.rerun()

            st.progress(
                progress / 100
            )

            st.caption(
                f"{progress}% complete"
            )

            with st.expander(
                "View AI Roadmap"
            ):

                st.markdown(
                    goal["roadmap"]
                    or "No roadmap available."
                )

            st.divider()

    else:

        st.info(
            "Create your first goal above."
        )

# =========================================================
# ANALYTICS
# =========================================================

elif page == "📊 Analytics":

    page_header(
        "Productivity Analytics",
        "Track completion, workload and productivity trends."
    )

    data = get_analytics()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Completed",
        data["completed"]
    )

    c2.metric(
        "Pending",
        data["pending"]
    )

    c3.metric(
        "Completion Rate",
        f"{data['completion_rate']}%"
    )

    c4.metric(
        "Active Goals",
        data["active_goals"]
    )

    st.markdown("### 📈 Productivity Trend")

    if data["daily"]:

        df = pd.DataFrame(
            data["daily"]
        )

        df["date"] = pd.to_datetime(
            df["date"]
        )

        fig = px.bar(
            df,
            x="date",
            y="completed",
            title="Completed Tasks Over Time"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "Complete some tasks to see your productivity trend."
        )

    st.markdown("### 📊 Task Distribution")

    if data["categories"]:

        category_df = pd.DataFrame(
            data["categories"]
        )

        fig2 = px.pie(
            category_df,
            names="category",
            values="count",
            hole=0.55,
            title="Tasks by Category"
        )

        fig2.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    else:

        st.info(
            "No task category data available yet."
        )

# =========================================================
# SETTINGS
# =========================================================

elif page == "⚙️ Settings":

    page_header(
        "Settings",
        "Personalize your LifeOS AI experience."
    )

    st.markdown("### 👤 Profile")

    display_name = st.text_input(
        "Display Name",
        value=get_preference(
            "display_name",
            ""
        )
    )

    timezone = st.selectbox(
        "Timezone",
        [
            "Asia/Karachi",
            "UTC",
            "Asia/Dubai",
            "Europe/London",
        ]
    )

    if st.button(
        "Save Preferences",
        use_container_width=True
    ):

        save_preference(
            "display_name",
            display_name.strip()
        )

        save_preference(
            "timezone",
            timezone
        )

        st.success(
            "Preferences saved successfully."
        )

    st.markdown("### 🤖 AI Configuration")

    st.code(
        'MODEL_NAME = "openai/gpt-oss-20b"',
        language="python"
    )

    st.caption(
        "The Groq model is configured in ai_engine.py."
    )

    st.markdown("### 🗄️ Database")

    st.info(
        "LifeOS AI uses SQLite for local data persistence."
    )

    st.markdown("### 🔐 Security")

    st.warning(
        "Never upload your real secrets.toml file or Groq API key to GitHub."
    )

    st.markdown("### ✦ About LifeOS AI")

    st.markdown(
        """
        **LifeOS AI** is a personal AI command center
        built with:

        • Python  
        • Streamlit  
        • SQLite  
        • Groq AI  
        • Plotly
        """
    )
