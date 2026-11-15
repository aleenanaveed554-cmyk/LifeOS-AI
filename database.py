import sqlite3
from datetime import datetime
from pathlib import Path

# =========================================================
# DATABASE CONFIG
# =========================================================

DB_PATH = Path(__file__).parent / "lifeos.db"


def get_connection():
    """Create and return a SQLite database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_db():
    """Create all required database tables."""

    conn = get_connection()
    cursor = conn.cursor()

    # -------------------------
    # TASKS TABLE
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT DEFAULT 'Other',
            priority TEXT DEFAULT 'Medium',
            deadline TEXT,
            completed INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    # -------------------------
    # GOALS TABLE
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            target_date TEXT,
            context TEXT,
            progress INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    # -------------------------
    # NOTES TABLE
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # -------------------------
    # STUDY PLANS TABLE
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            topics TEXT NOT NULL,
            exam_date TEXT,
            hours_per_day REAL DEFAULT 1,
            difficulty TEXT DEFAULT 'Medium',
            plan TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # -------------------------
    # PREFERENCES TABLE
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# TASK FUNCTIONS
# =========================================================

def add_task(
    title,
    category="Other",
    priority="Medium",
    deadline=None,
    completed=0
):
    """Add a new task."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks
        (title, category, priority, deadline, completed, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        title,
        category,
        priority,
        deadline,
        completed,
        datetime.now().isoformat()
    ))

    conn.commit()
    task_id = cursor.lastrowid
    conn.close()

    return task_id


def get_tasks():
    """Return all tasks."""

    conn = get_connection()

    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM tasks
        ORDER BY
            completed ASC,
            CASE priority
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low' THEN 3
                ELSE 4
            END,
            id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def update_task(task_id, completed=None, **kwargs):
    """Update a task."""

    conn = get_connection()
    cursor = conn.cursor()

    fields = []
    values = []

    if completed is not None:
        fields.append("completed = ?")
        values.append(int(completed))

    allowed_fields = [
        "title",
        "category",
        "priority",
        "deadline"
    ]

    for field in allowed_fields:
        if field in kwargs and kwargs[field] is not None:
            fields.append(f"{field} = ?")
            values.append(kwargs[field])

    if not fields:
        conn.close()
        return

    values.append(task_id)

    cursor.execute(
        f"""
        UPDATE tasks
        SET {", ".join(fields)}
        WHERE id = ?
        """,
        values
    )

    conn.commit()
    conn.close()


def delete_task(task_id):
    """Delete a task."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()
    conn.close()


# =========================================================
# GOAL FUNCTIONS
# =========================================================

def add_goal(
    title,
    target_date=None,
    context="",
    progress=0
):
    """Add a new goal."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO goals
        (title, target_date, context, progress, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        title,
        target_date,
        context,
        progress,
        datetime.now().isoformat()
    ))

    conn.commit()
    goal_id = cursor.lastrowid
    conn.close()

    return goal_id


def get_goals():
    """Return all goals."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM goals
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def update_goal(
    goal_id,
    progress=None,
    title=None,
    target_date=None,
    context=None
):
    """Update a goal."""

    conn = get_connection()
    cursor = conn.cursor()

    fields = []
    values = []

    if progress is not None:
        fields.append("progress = ?")
        values.append(int(progress))

    if title is not None:
        fields.append("title = ?")
        values.append(title)

    if target_date is not None:
        fields.append("target_date = ?")
        values.append(target_date)

    if context is not None:
        fields.append("context = ?")
        values.append(context)

    if not fields:
        conn.close()
        return

    values.append(goal_id)

    cursor.execute(
        f"""
        UPDATE goals
        SET {", ".join(fields)}
        WHERE id = ?
        """,
        values
    )

    conn.commit()
    conn.close()


# =========================================================
# NOTES FUNCTIONS
# =========================================================

def add_note(title, content):
    """Add a new note."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO notes
        (title, content, created_at)
        VALUES (?, ?, ?)
    """, (
        title,
        content,
        datetime.now().isoformat()
    ))

    conn.commit()
    note_id = cursor.lastrowid
    conn.close()

    return note_id


def get_notes():
    """Return all notes."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM notes
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def delete_note(note_id):
    """Delete a note."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM notes WHERE id = ?",
        (note_id,)
    )

    conn.commit()
    conn.close()


# =========================================================
# STUDY PLAN FUNCTIONS
# =========================================================

def add_study_plan(
    subject,
    topics,
    exam_date=None,
    hours_per_day=1,
    difficulty="Medium",
    plan=""
):
    """Save an AI-generated study plan."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO study_plans
        (
            subject,
            topics,
            exam_date,
            hours_per_day,
            difficulty,
            plan,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        subject,
        topics,
        exam_date,
        hours_per_day,
        difficulty,
        plan,
        datetime.now().isoformat()
    ))

    conn.commit()
    plan_id = cursor.lastrowid
    conn.close()

    return plan_id


def get_study_plans():
    """Return all saved study plans."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM study_plans
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# =========================================================
# PREFERENCES FUNCTIONS
# =========================================================

def save_preference(key, value):
    """Save or update a user preference."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO preferences (key, value)
        VALUES (?, ?)
        ON CONFLICT(key)
        DO UPDATE SET value = excluded.value
    """, (
        key,
        str(value)
    ))

    conn.commit()
    conn.close()


def get_preference(key, default=None):
    """Get a saved preference."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT value
        FROM preferences
        WHERE key = ?
    """, (key,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return row["value"]

    return default


# =========================================================
# ANALYTICS
# =========================================================

def get_analytics():
    """Return productivity analytics."""

    conn = get_connection()
    cursor = conn.cursor()

    # Total tasks
    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM tasks
    """)
    total_tasks = cursor.fetchone()["count"]

    # Completed tasks
    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM tasks
        WHERE completed = 1
    """)
    completed_tasks = cursor.fetchone()["count"]

    # Pending tasks
    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM tasks
        WHERE completed = 0
    """)
    pending_tasks = cursor.fetchone()["count"]

    # High priority pending tasks
    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM tasks
        WHERE completed = 0
        AND priority = 'High'
    """)
    high_priority_tasks = cursor.fetchone()["count"]

    # Total goals
    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM goals
    """)
    total_goals = cursor.fetchone()["count"]

    # Average goal progress
    cursor.execute("""
        SELECT COALESCE(AVG(progress), 0) AS average
        FROM goals
    """)
    average_goal_progress = cursor.fetchone()["average"]

    # Total notes
    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM notes
    """)
    total_notes = cursor.fetchone()["count"]

    # Total study plans
    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM study_plans
    """)
    total_study_plans = cursor.fetchone()["count"]

    # Study hours
    cursor.execute("""
        SELECT COALESCE(SUM(hours_per_day), 0) AS hours
        FROM study_plans
    """)
    study_hours = cursor.fetchone()["hours"]

    conn.close()

    completion_rate = (
        (completed_tasks / total_tasks) * 100
        if total_tasks > 0
        else 0
    )

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "high_priority_tasks": high_priority_tasks,
        "total_goals": total_goals,
        "average_goal_progress": round(
            average_goal_progress, 1
        ),
        "total_notes": total_notes,
        "total_study_plans": total_study_plans,
        "study_hours": round(study_hours, 1),
        "completion_rate": round(
            completion_rate, 1
        )
    }


# =========================================================
# OPTIONAL: CLEAR DATABASE
# =========================================================

def clear_all_data():
    """
    Delete all application data.
    Useful for development/testing.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks")
    cursor.execute("DELETE FROM goals")
    cursor.execute("DELETE FROM notes")
    cursor.execute("DELETE FROM study_plans")
    cursor.execute("DELETE FROM preferences")

    conn.commit()
    conn.close()


# =========================================================
# AUTO INITIALIZE
# =========================================================

init_db()
