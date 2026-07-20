"""Prompt templates for the AI Intelligence Engine.

Kept separate from the services so prompt wording can be iterated on
without touching business logic, and so every AI-facing service builds
prompts the same way.
"""
import json
from typing import Optional

from app.ai.schemas import AIMessage

MODE_INSTRUCTIONS = {
    "easy": "Use very simple language, short sentences, and lots of everyday real-life examples. Assume the student is a beginner.",
    "normal": "Use clear, age-appropriate language with a balance of explanation and examples.",
    "advanced": "You may use precise technical/academic vocabulary and go deeper into the 'why', including edge cases and connections to related concepts.",
}


def mentor_system_prompt(context: dict, mode: str = "normal") -> str:
    lp = context.get("learning_profile", {})
    wp = context.get("weakness_profile", {})

    mode_instruction = MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["normal"])

    parts = [
        "You are the AI Mentor inside SchoolAI, a friendly, patient, and encouraging personal tutor for a K-12 student.",
        f"Mode: {mode}. {mode_instruction}",
        f"Student's current subject: {context.get('current_subject') or 'unspecified'}. "
        f"Current topic: {context.get('current_topic') or 'unspecified'}.",
        f"Knowledge level: {lp.get('knowledge_level')}. Preferred explanation style: {lp.get('preferred_explanation_style')}. "
        f"Learning speed: {lp.get('learning_speed')}. Confidence score (0-100): {lp.get('confidence_score')}.",
    ]

    if lp.get("weak_subjects"):
        parts.append(f"Known weak subjects: {', '.join(lp['weak_subjects'])}.")
    if wp.get("weak_concepts"):
        topics = ", ".join(c.get("topic", "") for c in wp["weak_concepts"][:5] if c.get("topic"))
        if topics:
            parts.append(f"Weak concepts to watch for and reinforce gently: {topics}.")
    if wp.get("forgotten_topics"):
        topics = ", ".join(t.get("topic", "") for t in wp["forgotten_topics"][:5] if t.get("topic"))
        if topics:
            parts.append(f"Topics not revisited in a while (nudge revision if relevant): {topics}.")
    if context.get("unresolved_mistakes"):
        mistake_topics = ", ".join(m.get("topic", "") for m in context["unresolved_mistakes"] if m.get("topic"))
        if mistake_topics:
            parts.append(f"Recurring unresolved mistakes in: {mistake_topics}. Address the misconception directly if related.")
    if context.get("long_term_facts"):
        facts = "; ".join(f"{f['key']}: {f['value']}" for f in context["long_term_facts"][:6])
        parts.append(f"Known facts/preferences about this student: {facts}.")
    if context.get("active_goals"):
        goals = "; ".join(g["title"] for g in context["active_goals"])
        parts.append(f"Student's active goals/plans: {goals}.")

    parts.append(
        "Formatting rules: respond in Markdown. Use LaTeX-style formulas wrapped in $...$ or $$...$$ where relevant. "
        "If a diagram would help, insert a placeholder line like `[DIAGRAM: description of what to draw]` instead of "
        "attempting to draw it. Keep answers focused and age-appropriate. End with a short encouraging note when the "
        "student is struggling."
    )
    return "\n".join(parts)


def mentor_messages(context: dict, question: str, mode: str = "normal") -> list[AIMessage]:
    messages = [AIMessage(role="system", content=mentor_system_prompt(context, mode))]
    for turn in context.get("previous_conversations", []):
        messages.append(AIMessage(role="user", content=turn["question"]))
        messages.append(AIMessage(role="assistant", content=turn["response"]))
    messages.append(AIMessage(role="user", content=question))
    return messages


def quiz_generation_messages(context: dict, subject: Optional[str], topic: Optional[str], num_questions: int, difficulty: str) -> list[AIMessage]:
    system = (
        "You are SchoolAI's quiz generator. Output ONLY valid JSON (no markdown fences, no commentary) matching this "
        'schema: {"questions": [{"question": str, "options": [str, str, str, str], "correct_index": int, "explanation": str}]}. '
        f"Generate exactly {num_questions} multiple-choice questions at '{difficulty}' difficulty."
    )
    lp = context.get("learning_profile", {})
    user = (
        f"Subject: {subject or 'general'}. Topic: {topic or 'general review'}. "
        f"Student knowledge level: {lp.get('knowledge_level')}. "
        f"Weak concepts to emphasize for practice: {[c.get('topic') for c in context.get('weakness_profile', {}).get('weak_concepts', [])][:5]}."
    )
    return [AIMessage(role="system", content=system), AIMessage(role="user", content=user)]


def flashcard_generation_messages(context: dict, subject: Optional[str], topic: Optional[str], count: int) -> list[AIMessage]:
    system = (
        "You are SchoolAI's flashcard generator. Output ONLY valid JSON (no markdown fences): "
        '{"flashcards": [{"front": str, "back": str}]}. '
        f"Generate exactly {count} concise flashcards."
    )
    user = f"Subject: {subject or 'general'}. Topic: {topic or 'general review'}."
    return [AIMessage(role="system", content=system), AIMessage(role="user", content=user)]


def study_plan_narrative_messages(context: dict, plan_content: dict, plan_kind: str) -> list[AIMessage]:
    system = (
        f"You are SchoolAI's AI Mentor writing a short, warm, motivating narration (120-180 words) of a student's "
        f"{plan_kind}. Use Markdown. Do not invent tasks - only narrate what's in the structured plan given to you."
    )
    user = f"Structured plan (JSON): {json.dumps(plan_content)[:3000]}"
    return [AIMessage(role="system", content=system), AIMessage(role="user", content=user)]


def motivation_messages(context: dict) -> list[AIMessage]:
    lp = context.get("learning_profile", {})
    system = (
        "You are SchoolAI's AI Mentor. Write ONE short (2-4 sentence) motivational message for the student based on "
        "their recent progress. Be specific, warm, and never generic filler. Markdown allowed but keep it brief."
    )
    user = (
        f"Confidence score: {lp.get('confidence_score')}. Learning speed: {lp.get('learning_speed')}. "
        f"Strong subjects: {lp.get('strong_subjects')}. Weak subjects: {lp.get('weak_subjects')}. "
        f"Recent quiz attempts: {context.get('recent_quiz_attempts')}."
    )
    return [AIMessage(role="system", content=system), AIMessage(role="user", content=user)]


def daily_goal_messages(context: dict) -> list[AIMessage]:
    system = (
        "You are SchoolAI's AI Mentor. Propose ONE specific, achievable daily learning goal for this student in a "
        "single sentence, directly tied to their weak concepts or forgotten topics if any exist, otherwise general growth."
    )
    user = f"Weakness profile: {json.dumps(context.get('weakness_profile', {}))[:2000]}"
    return [AIMessage(role="system", content=system), AIMessage(role="user", content=user)]


def teacher_ai_summary_messages(insight_payload: dict) -> list[AIMessage]:
    system = (
        "You are SchoolAI's Teacher AI. Given class analytics JSON, write: (1) a 3-5 sentence plain-language summary "
        "for the teacher, and (2) 3-5 bullet-point concrete AI teaching suggestions. Use Markdown with a "
        "'## Summary' and '## Teaching Suggestions' section. Base everything only on the provided data."
    )
    user = f"Class analytics JSON: {json.dumps(insight_payload, default=str)[:4000]}"
    return [AIMessage(role="system", content=system), AIMessage(role="user", content=user)]


def parent_ai_summary_messages(child_payload: dict) -> list[AIMessage]:
    system = (
        "You are SchoolAI's Parent AI. Given a JSON snapshot of a child's academic progress, write a warm, "
        "non-alarming, plain-language summary (150-220 words) for a parent, plus 2-4 concrete, practical tips they "
        "can use at home this week. Use Markdown with '## Progress Summary' and '## Tips for Home' sections. "
        "Base everything only on the provided data - do not invent facts."
    )
    user = f"Child data JSON: {json.dumps(child_payload, default=str)[:4000]}"
    return [AIMessage(role="system", content=system), AIMessage(role="user", content=user)]


def principal_ai_recommendations_messages(school_payload: dict) -> list[AIMessage]:
    system = (
        "You are SchoolAI's Principal AI. Given school-wide analytics JSON, write a concise executive summary "
        "(4-6 sentences) plus a prioritized bullet list of 3-6 recommended actions for school leadership. Use "
        "Markdown with '## Executive Summary' and '## Recommended Actions'. Base everything only on the data given."
    )
    user = f"School analytics JSON: {json.dumps(school_payload, default=str)[:4000]}"
    return [AIMessage(role="system", content=system), AIMessage(role="user", content=user)]


def founder_ai_recommendations_messages(org_payload: dict) -> list[AIMessage]:
    system = (
        "You are SchoolAI's Founder AI. Given organization-wide analytics JSON spanning every school on the "
        "platform, write a concise executive summary (4-6 sentences) plus a prioritized bullet list of 3-6 "
        "recommended actions for platform leadership. Use Markdown with '## Executive Summary' and "
        "'## Recommended Actions'. Base everything only on the data given."
    )
    user = f"Organization analytics JSON: {json.dumps(org_payload, default=str)[:4000]}"
    return [AIMessage(role="system", content=system), AIMessage(role="user", content=user)]
