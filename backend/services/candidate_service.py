import requests

from app.config import settings


def build_fallback_summary(candidate, scores):
    score_text = "No scores yet"
    if scores:
        average = sum(score.score for score in scores) / len(scores)
        categories = ", ".join(sorted({score.category for score in scores}))
        score_text = f"{len(scores)} visible score(s), average {average:.1f}/5 across {categories}"

    return (
        f"{candidate.name} is being reviewed for {candidate.role_applied}. "
        f"Skills: {', '.join(candidate.skills or []) or 'not listed'}. {score_text}."
    )


def generate_ai_summary(candidate, scores):
    if not settings.groq_api_key:
        return build_fallback_summary(candidate, scores)

    score_lines = [
        f"- {score.category}: {score.score}/5"
        + (f" ({score.note})" if score.note else "")
        for score in scores
    ]
    prompt = f"""
Create a concise recruitment review summary for this candidate.

Candidate:
- Name: {candidate.name}
- Email: {candidate.email}
- Role applied: {candidate.role_applied}
- Status: {candidate.status.value}
- Skills: {", ".join(candidate.skills or []) or "None listed"}
- Internal notes: {candidate.internal_notes or "None"}

Visible scores:
{chr(10).join(score_lines) if score_lines else "- No scores yet"}

Write 3-5 sentences. Mention strengths, concerns, and next step. Do not invent facts.
""".strip()

    payload = {
        "model": settings.groq_model,
        "messages": [
            {
                "role": "system",
                "content": "You summarize candidate review data for an internal recruiting dashboard.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.2,
        "max_completion_tokens": 260,
    }
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.groq_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise RuntimeError("Groq summary generation failed") from exc

    choices = data.get("choices") or []
    if choices:
        content = choices[0].get("message", {}).get("content")
        if content:
            return content.strip()

    raise RuntimeError("Groq summary response did not include text")
