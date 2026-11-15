import os
import json
import streamlit as st
from groq import Groq


# =========================================================
# GROQ CONFIGURATION
# =========================================================

# Model ko sirf yahan se change karna hoga
MODEL_NAME = "openai/gpt-oss-20b"


def get_api_key():
    """
    Get Groq API key securely from Streamlit secrets
    or environment variables.
    """

    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        api_key = None

    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")

    return api_key


def get_client():
    """Create Groq client."""

    api_key = get_api_key()

    if not api_key:
        raise ValueError(
            "Groq API key not found. "
            "Please add GROQ_API_KEY to Streamlit Secrets."
        )

    return Groq(api_key=api_key)


# =========================================================
# GENERIC AI CHAT
# =========================================================

def ai_chat(
    user_message,
    system_prompt=None,
    temperature=0.7,
    max_tokens=1200
):
    """
    Send a message to Groq and return AI response.
    """

    try:
        client = get_client()

        if not system_prompt:
            system_prompt = """
You are LifeOS AI, a helpful personal productivity assistant.

Help the user with:
- Daily planning
- Task management
- Study planning
- Goal setting
- Notes
- Productivity
- Time management

Always give clear, practical and structured answers.
Use headings and bullet points when useful.
Keep the response easy to understand.
"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"AI Error: {str(e)}"


# =========================================================
# AI DAILY PLANNER
# =========================================================

def generate_daily_plan(
    activities,
    available_time,
    priorities,
    deadlines
):
    """
    Generate a structured daily plan.
    """

    prompt = f"""
Create a realistic daily productivity plan.

USER ACTIVITIES:
{activities}

AVAILABLE TIME:
{available_time}

PRIORITIES:
{priorities}

DEADLINES:
{deadlines}

Create a clear schedule.

Include:

1. Today's priorities
2. Recommended task order
3. Time estimate for every task
4. Breaks
5. Important deadlines
6. Tasks that can be postponed
7. Short productivity tips

Make the plan practical and achievable.
Do not overload the user.
"""

    return ai_chat(
        prompt,
        system_prompt="""
You are an expert personal productivity planner.

Create realistic schedules.
Avoid overloading the user.
Prioritize urgent and important work.
Use clear headings, bullet points and time blocks.
""",
        temperature=0.6,
        max_tokens=1400
    )


# =========================================================
# AI STUDY PLANNER
# =========================================================

def generate_study_plan(
    subject,
    topics,
    exam_date,
    hours_per_day,
    difficulty
):
    """
    Generate an AI study plan.
    """

    prompt = f"""
Create a detailed study plan for the following student.

SUBJECT:
{subject}

TOPICS / CHAPTERS:
{topics}

EXAM DATE:
{exam_date}

AVAILABLE STUDY HOURS PER DAY:
{hours_per_day}

DIFFICULTY:
{difficulty}

Create a realistic study roadmap.

Include:

1. Daily study schedule
2. Topics to study each day
3. Important topics
4. Revision sessions
5. Practice sessions
6. Self-testing / quiz sessions
7. Final revision before exam
8. Study tips

Keep the workload realistic according to the available hours.
"""

    return ai_chat(
        prompt,
        system_prompt="""
You are an expert academic study planner.

Create structured and realistic study plans.
Break large topics into smaller sessions.
Include revision and practice.
Prioritize difficult and important topics.
""",
        temperature=0.6,
        max_tokens=1600
    )


# =========================================================
# AI NOTES ANALYZER
# =========================================================

def analyze_notes(note_text):
    """
    Analyze notes and generate useful study material.
    """

    prompt = f"""
Analyze the following notes:

-------------------------
NOTES
-------------------------

{note_text}

-------------------------

Create a useful study guide.

Include these sections:

1. Summary
2. Key Points
3. Important Concepts
4. Important Terms
5. Flashcards
6. Quiz Questions
7. Action Items / Things to Remember

Make the explanation clear and easy to study.
"""

    return ai_chat(
        prompt,
        system_prompt="""
You are an expert note-taking and study assistant.

Transform messy notes into clear and organized learning material.

Use headings.
Use bullet points.
Create useful flashcards and quiz questions.
Do not remove important information.
""",
        temperature=0.5,
        max_tokens=1800
    )


# =========================================================
# AI GOAL BREAKDOWN
# =========================================================

def breakdown_goal(
    goal_title,
    target_date,
    context
):
    """
    Break a large goal into milestones and actions.
    """

    prompt = f"""
Break the following goal into an actionable roadmap.

GOAL:
{goal_title}

TARGET DATE:
{target_date}

ADDITIONAL CONTEXT:
{context}

Create:

1. Main Goal
2. Why this goal matters
3. Major Milestones
4. Weekly Targets
5. Daily Actions
6. Possible Challenges
7. How to measure progress
8. First 3 actions to start with

Make the plan realistic and achievable.
"""

    return ai_chat(
        prompt,
        system_prompt="""
You are an expert goal-setting coach.

Turn large goals into small actionable steps.
Use milestones, weekly targets and daily actions.
Keep goals realistic and measurable.
""",
        temperature=0.6,
        max_tokens=1500
    )


# =========================================================
# AI PRODUCTIVITY RECOMMENDATIONS
# =========================================================

def generate_productivity_recommendations(
    tasks,
    goals,
    study_plans
):
    """
    Generate personalized productivity recommendations.
    """

    prompt = f"""
Analyze the user's current productivity data.

TASKS:
{tasks}

GOALS:
{goals}

STUDY PLANS:
{study_plans}

Give personalized recommendations.

Include:

1. What should be done first
2. Tasks that need attention
3. Productivity improvements
4. Study recommendations
5. Goal recommendations
6. Time-management advice
7. One small action the user can take today

Keep recommendations practical and concise.
"""

    return ai_chat(
        prompt,
        system_prompt="""
You are LifeOS AI's productivity analyst.

Analyze tasks, goals and study plans.
Give practical recommendations based on the provided information.
Do not make unrealistic assumptions.
""",
        temperature=0.6,
        max_tokens=1200
    )


# =========================================================
# SIMPLE JSON AI RESPONSE
# =========================================================

def ai_json(prompt, system_prompt=None):
    """
    Ask the model for JSON output.

    Useful for future structured AI features.
    """

    if not system_prompt:
        system_prompt = """
Return only valid JSON.
Do not use markdown.
Do not add explanations outside JSON.
"""

    response = ai_chat(
        prompt,
        system_prompt=system_prompt,
        temperature=0.2,
        max_tokens=1200
    )

    try:
        return json.loads(response)

    except json.JSONDecodeError:
        # Try removing markdown code fences
        cleaned = response.replace("```json", "")
        cleaned = cleaned.replace("```", "")
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except Exception:
            return {
                "error": "AI returned invalid JSON",
                "raw_response": response
            }


# =========================================================
# API STATUS CHECK
# =========================================================

def check_ai_connection():
    """
    Check whether Groq API is configured correctly.
    """

    try:
        api_key = get_api_key()

        if not api_key:
            return False, "Groq API key is missing."

        client = get_client()

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": "Reply with the word OK."
                }
            ],
            temperature=0,
            max_tokens=10
        )

        if response.choices:
            return True, "Groq AI connection is working."

        return False, "No response received from Groq."

    except Exception as e:
        return False, f"Connection failed: {str(e)}"
