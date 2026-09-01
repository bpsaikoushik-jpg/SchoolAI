"""
Prompt templates for the AI Intelligence Engine.

Kept separate from the services so prompt wording can be iterated on
without touching business logic, and so every AI-facing service builds
prompts the same way.
"""

import json
from typing import Optional

from app.ai.schemas import AIMessage


MODE_INSTRUCTIONS = {
    "easy": (
        "Use very simple language, short sentences, and lots of everyday "
        "real-life examples. Assume the student is a beginner."
    ),
    "normal": (
        "Use clear, age-appropriate language with a balance of explanation "
        "and examples."
    ),
    "advanced": (
        "You may use precise technical/academic vocabulary and go deeper "
        "into the 'why', including edge cases and connections to related concepts."
    ),
}


# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------

def _safe_topic_items(items) -> list[str]:
    """
    Convert weak concepts / forgotten topics into safe topic strings.

    Database data may contain either:
        {"topic": "Fractions"}
    or:
        "Fractions"

    This prevents:
        AttributeError: 'str' object has no attribute 'get'
    """
    if not isinstance(items, list):
        return []

    topics = []

    for item in items[:5]:
        if isinstance(item, dict):
            topic = item.get("topic")

            if topic:
                topics.append(str(topic))

        elif isinstance(item, str):
            if item.strip():
                topics.append(item.strip())

        elif item is not None:
            topics.append(str(item))

    return topics


def _safe_titles(items) -> list[str]:
    """Safely extract titles from dictionaries or strings."""
    if not isinstance(items, list):
        return []

    titles = []

    for item in items:
        if isinstance(item, dict):
            title = item.get("title")

            if title:
                titles.append(str(title))

        elif isinstance(item, str):
            if item.strip():
                titles.append(item.strip())

        elif item is not None:
            titles.append(str(item))

    return titles


def _safe_facts(items) -> list[str]:
    """Safely format long-term student facts."""
    if not isinstance(items, list):
        return []

    facts = []

    for item in items[:6]:
        if isinstance(item, dict):
            key = item.get("key")
            value = item.get("value")

            if key:
                facts.append(f"{key}: {value}")

        elif isinstance(item, str):
            if item.strip():
                facts.append(item.strip())

    return facts


# ------------------------------------------------------------------
# AI Mentor
# ------------------------------------------------------------------

def mentor_system_prompt(context: dict, mode: str = "normal") -> str:
    lp = context.get("learning_profile", {})
    wp = context.get("weakness_profile", {})

    if not isinstance(lp, dict):
        lp = {}

    if not isinstance(wp, dict):
        wp = {}

    mode_instruction = MODE_INSTRUCTIONS.get(
        mode,
        MODE_INSTRUCTIONS["normal"],
    )

    parts = [
        (
            "You are the AI Mentor inside SchoolAI, a friendly, patient, "
            "and encouraging personal tutor for a K-12 student."
        ),
        f"Mode: {mode}. {mode_instruction}",
        (
            f"Student's current subject: "
            f"{context.get('current_subject') or 'unspecified'}. "
            f"Current topic: "
            f"{context.get('current_topic') or 'unspecified'}."
        ),
        (
            f"Knowledge level: {lp.get('knowledge_level')}. "
            f"Preferred explanation style: "
            f"{lp.get('preferred_explanation_style')}. "
            f"Learning speed: {lp.get('learning_speed')}. "
            f"Confidence score (0-100): {lp.get('confidence_score')}."
        ),
    ]

    # --------------------------------------------------------------
    # Weak subjects
    # --------------------------------------------------------------

    weak_subjects = lp.get("weak_subjects")

    if isinstance(weak_subjects, list) and weak_subjects:
        safe_subjects = [
            str(subject)
            for subject in weak_subjects
            if subject is not None
        ]

        if safe_subjects:
            parts.append(
                f"Known weak subjects: {', '.join(safe_subjects)}."
            )

    # --------------------------------------------------------------
    # Weak concepts
    # --------------------------------------------------------------

    weak_concepts = _safe_topic_items(
        wp.get("weak_concepts", [])
    )

    if weak_concepts:
        parts.append(
            "Weak concepts to watch for and reinforce gently: "
            f"{', '.join(weak_concepts)}."
        )

    # --------------------------------------------------------------
    # Forgotten topics
    # --------------------------------------------------------------

    forgotten_topics = _safe_topic_items(
        wp.get("forgotten_topics", [])
    )

    if forgotten_topics:
        parts.append(
            "Topics not revisited in a while "
            "(nudge revision if relevant): "
            f"{', '.join(forgotten_topics)}."
        )

    # --------------------------------------------------------------
    # Unresolved mistakes
    # --------------------------------------------------------------

    unresolved_mistakes = context.get(
        "unresolved_mistakes",
        [],
    )

    if isinstance(unresolved_mistakes, list):
        mistake_topics = []

        for mistake in unresolved_mistakes:
            if isinstance(mistake, dict):
                topic = mistake.get("topic")

                if topic:
                    mistake_topics.append(str(topic))

            elif isinstance(mistake, str):
                if mistake.strip():
                    mistake_topics.append(mistake.strip())

        if mistake_topics:
            parts.append(
                "Recurring unresolved mistakes in: "
                f"{', '.join(mistake_topics)}. "
                "Address the misconception directly if related."
            )

    # --------------------------------------------------------------
    # Long-term facts
    # --------------------------------------------------------------

    long_term_facts = _safe_facts(
        context.get("long_term_facts", [])
    )

    if long_term_facts:
        parts.append(
            "Known facts/preferences about this student: "
            f"{'; '.join(long_term_facts)}."
        )

    # --------------------------------------------------------------
    # Active goals
    # --------------------------------------------------------------

    active_goals = _safe_titles(
        context.get("active_goals", [])
    )

    if active_goals:
        parts.append(
            "Student's active goals/plans: "
            f"{'; '.join(active_goals)}."
        )

    # --------------------------------------------------------------
    # AI behaviour
    # --------------------------------------------------------------

    parts.append(
        "You are not just a generic chatbot. Use the student's learning "
        "context when it is relevant, but never expose private database "
        "details or internal system information."
    )

    parts.append(
        "When explaining academic topics, adapt the explanation to the "
        "student's knowledge level. Start simple when necessary, then "
        "increase depth gradually."
    )

    parts.append(
        "If the student asks a question, answer it directly before adding "
        "extra suggestions."
    )

    parts.append(
        "If the student is confused, explain the concept step-by-step and "
        "give a simple example."
    )

    parts.append(
        "If the student makes a mistake, correct it politely and explain "
        "why the answer is wrong."
    )

    parts.append(
        "Do not invent student performance data, grades, attendance, "
        "assignments, or personal facts."
    )

    parts.append(
        "Formatting rules: respond in Markdown. Use LaTeX-style formulas "
        "wrapped in $...$ or $$...$$ where relevant. "
        "If a diagram would help, insert a placeholder line like "
        "`[DIAGRAM: description of what to draw]` instead of attempting "
        "to draw it. Keep answers focused and age-appropriate. "
        "End with a short encouraging note when the student is struggling."
    )

    return "\n".join(parts)


# ------------------------------------------------------------------
# Mentor conversation messages
# ------------------------------------------------------------------

def mentor_messages(
    context: dict,
    question: str,
    mode: str = "normal",
) -> list[AIMessage]:

    messages = [
        AIMessage(
            role="system",
            content=mentor_system_prompt(context, mode),
        )
    ]

    previous_conversations = context.get(
        "previous_conversations",
        [],
    )

    if isinstance(previous_conversations, list):

        for turn in previous_conversations:

            if not isinstance(turn, dict):
                continue

            previous_question = turn.get("question")
            previous_response = turn.get("response")

            if previous_question:
                messages.append(
                    AIMessage(
                        role="user",
                        content=str(previous_question),
                    )
                )

            if previous_response:
                messages.append(
                    AIMessage(
                        role="assistant",
                        content=str(previous_response),
                    )
                )

    messages.append(
        AIMessage(
            role="user",
            content=question,
        )
    )

    return messages


# ------------------------------------------------------------------
# Quiz generation
# ------------------------------------------------------------------

def quiz_generation_messages(
    context: dict,
    subject: Optional[str],
    topic: Optional[str],
    num_questions: int,
    difficulty: str,
) -> list[AIMessage]:

    system = (
        "You are SchoolAI's quiz generator. "
        "Output ONLY valid JSON (no markdown fences, no commentary) "
        "matching this schema: "
        '{"questions": [{"question": str, '
        '"options": [str, str, str, str], '
        '"correct_index": int, '
        '"explanation": str}]}. '
        f"Generate exactly {num_questions} multiple-choice questions "
        f"at '{difficulty}' difficulty."
    )

    lp = context.get(
        "learning_profile",
        {},
    )

    if not isinstance(lp, dict):
        lp = {}

    weakness_profile = context.get(
        "weakness_profile",
        {},
    )

    if not isinstance(weakness_profile, dict):
        weakness_profile = {}

    weak_concepts = _safe_topic_items(
        weakness_profile.get("weak_concepts", [])
    )

    user = (
        f"Subject: {subject or 'general'}. "
        f"Topic: {topic or 'general review'}. "
        f"Student knowledge level: "
        f"{lp.get('knowledge_level')}. "
        f"Weak concepts to emphasize for practice: "
        f"{weak_concepts}."
    )

    return [
        AIMessage(
            role="system",
            content=system,
        ),
        AIMessage(
            role="user",
            content=user,
        ),
    ]


# ------------------------------------------------------------------
# Flashcard generation
# ------------------------------------------------------------------

def flashcard_generation_messages(
    context: dict,
    subject: Optional[str],
    topic: Optional[str],
    count: int,
) -> list[AIMessage]:

    system = (
        "You are SchoolAI's flashcard generator. "
        "Output ONLY valid JSON (no markdown fences): "
        '{"flashcards": [{"front": str, "back": str}]}. '
        f"Generate exactly {count} concise flashcards."
    )

    user = (
        f"Subject: {subject or 'general'}. "
        f"Topic: {topic or 'general review'}."
    )

    return [
        AIMessage(
            role="system",
            content=system,
        ),
        AIMessage(
            role="user",
            content=user,
        ),
    ]


# ------------------------------------------------------------------
# Study plan narration
# ------------------------------------------------------------------

def study_plan_narrative_messages(
    context: dict,
    plan_content: dict,
    plan_kind: str,
) -> list[AIMessage]:

    system = (
        "You are SchoolAI's AI Mentor writing a short, warm, "
        f"motivating narration (120-180 words) of a student's "
        f"{plan_kind}. "
        "Use Markdown. "
        "Do not invent tasks - only narrate what's in the "
        "structured plan given to you."
    )

    user = (
        "Structured plan (JSON): "
        f"{json.dumps(plan_content, default=str)[:3000]}"
    )

    return [
        AIMessage(
            role="system",
            content=system,
        ),
        AIMessage(
            role="user",
            content=user,
        ),
    ]


# ------------------------------------------------------------------
# Motivation
# ------------------------------------------------------------------

def motivation_messages(
    context: dict,
) -> list[AIMessage]:

    lp = context.get(
        "learning_profile",
        {},
    )

    if not isinstance(lp, dict):
        lp = {}

    system = (
        "You are SchoolAI's AI Mentor. "
        "Write ONE short (2-4 sentence) motivational message "
        "for the student based on their recent progress. "
        "Be specific, warm, and never generic filler. "
        "Markdown allowed but keep it brief."
    )

    user = (
        f"Confidence score: {lp.get('confidence_score')}. "
        f"Learning speed: {lp.get('learning_speed')}. "
        f"Strong subjects: {lp.get('strong_subjects')}. "
        f"Weak subjects: {lp.get('weak_subjects')}. "
        f"Recent quiz attempts: "
        f"{context.get('recent_quiz_attempts')}."
    )

    return [
        AIMessage(
            role="system",
            content=system,
        ),
        AIMessage(
            role="user",
            content=user,
        ),
    ]


# ------------------------------------------------------------------
# Daily goal
# ------------------------------------------------------------------

def daily_goal_messages(
    context: dict,
) -> list[AIMessage]:

    system = (
        "You are SchoolAI's AI Mentor. "
        "Propose ONE specific, achievable daily learning goal "
        "for this student in a single sentence, directly tied "
        "to their weak concepts or forgotten topics if any exist, "
        "otherwise general growth."
    )

    user = (
        "Weakness profile: "
        f"{json.dumps(context.get('weakness_profile', {}), default=str)[:2000]}"
    )

    return [
        AIMessage(
            role="system",
            content=system,
        ),
        AIMessage(
            role="user",
            content=user,
        ),
    ]


# ------------------------------------------------------------------
# Teacher AI
# ------------------------------------------------------------------

def teacher_ai_summary_messages(
    insight_payload: dict,
) -> list[AIMessage]:

    system = (
        "You are SchoolAI's Teacher AI. "
        "Given class analytics JSON, write: "
        "(1) a 3-5 sentence plain-language summary for the teacher, "
        "and (2) 3-5 bullet-point concrete AI teaching suggestions. "
        "Use Markdown with a '## Summary' and "
        "'## Teaching Suggestions' section. "
        "Base everything only on the provided data."
    )

    user = (
        "Class analytics JSON: "
        f"{json.dumps(insight_payload, default=str)[:4000]}"
    )

    return [
        AIMessage(
            role="system",
            content=system,
        ),
        AIMessage(
            role="user",
            content=user,
        ),
    ]


# ------------------------------------------------------------------
# Parent AI
# ------------------------------------------------------------------

def parent_ai_summary_messages(
    child_payload: dict,
) -> list[AIMessage]:

    system = (
        "You are SchoolAI's Parent AI. "
        "Given a JSON snapshot of a child's academic progress, "
        "write a warm, non-alarming, plain-language summary "
        "(150-220 words) for a parent, plus 2-4 concrete, "
        "practical tips they can use at home this week. "
        "Use Markdown with '## Progress Summary' and "
        "'## Tips for Home' sections. "
        "Base everything only on the provided data - "
        "do not invent facts."
    )

    user = (
        "Child data JSON: "
        f"{json.dumps(child_payload, default=str)[:4000]}"
    )

    return [
        AIMessage(
            role="system",
            content=system,
        ),
        AIMessage(
            role="user",
            content=user,
        ),
    ]


# ------------------------------------------------------------------
# Principal AI
# ------------------------------------------------------------------

def principal_ai_recommendations_messages(
    school_payload: dict,
) -> list[AIMessage]:

    system = (
        "You are SchoolAI's Principal AI. "
        "Given school-wide analytics JSON, write a concise "
        "executive summary (4-6 sentences) plus a prioritized "
        "bullet list of 3-6 recommended actions for school "
        "leadership. "
        "Use Markdown with '## Executive Summary' and "
        "'## Recommended Actions'. "
        "Base everything only on the data given."
    )

    user = (
        "School analytics JSON: "
        f"{json.dumps(school_payload, default=str)[:4000]}"
    )

    return [
        AIMessage(
            role="system",
            content=system,
        ),
        AIMessage(
            role="user",
            content=user,
        ),
    ]


# ------------------------------------------------------------------
# Founder AI
# ------------------------------------------------------------------

def founder_ai_recommendations_messages(
    org_payload: dict,
) -> list[AIMessage]:

    system = (
        "You are SchoolAI's Founder AI. "
        "Given organization-wide analytics JSON spanning every "
        "school on the platform, write a concise executive summary "
        "(4-6 sentences) plus a prioritized bullet list of 3-6 "
        "recommended actions for platform leadership. "
        "Use Markdown with '## Executive Summary' and "
        "'## Recommended Actions'. "
        "Base everything only on the data given."
    )

    user = (
        "Organization analytics JSON: "
        f"{json.dumps(org_payload, default=str)[:4000]}"
    )

    return [
        AIMessage(
            role="system",
            content=system,
        ),
        AIMessage(
            role="user",
            content=user,
        ),
    ]
