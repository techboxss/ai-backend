from typing import Any

from modules.ollama_client import generate_json_from_ollama
from shared.prompts.triage_prompt import build_triage_prompt
from shared.schemas.triage_schema import EmailForTriage, TriageResponse


LEVEL_VALUES = {"High", "Medium", "Low"}

CLASSIFICATION_VALUES = {
    "Closings",
    "Documents",
    "Counterparty",
    "Court/Docket",
    "Newsletter/CLE",
    "General Client Communication",
}

PROPERTY_STATUS_VALUES = {
    "UNDERWAY",
    "AT RISK",
    "DELAYED",
    "CLOSED",
    "UNKNOWN",
}


def _clean_choice(value: Any, allowed: set[str], field_name: str) -> str:
    """
    Validate a single-choice Ollama field.

    This is not fallback triage.
    The triage result still comes from Ollama only.
    This only rejects malformed enum outputs before Pydantic validation.
    """
    cleaned = str(value or "").strip()

    if cleaned in allowed:
        return cleaned

    raise ValueError(
        f"Ollama returned invalid {field_name}: {cleaned!r}. "
        f"Expected exactly one of: {', '.join(sorted(allowed))}."
    )


def _normalize_ollama_result(result: dict[str, Any]) -> dict[str, Any]:
    """
    Strictly validate Ollama's enum-like fields.

    No rule-based fallback is used.
    If Ollama returns bad values, this raises an error.
    """
    if not isinstance(result, dict):
        raise ValueError("Ollama response must be a JSON object.")

    result["classification"] = _clean_choice(
        result.get("classification"),
        CLASSIFICATION_VALUES,
        "classification",
    )

    result["confidence"] = _clean_choice(
        result.get("confidence"),
        LEVEL_VALUES,
        "confidence",
    )

    result["priority"] = _clean_choice(
        result.get("priority"),
        LEVEL_VALUES,
        "priority",
    )

    property_transaction = result.get("property_transaction")

    if isinstance(property_transaction, dict):
        property_transaction["status"] = _clean_choice(
            property_transaction.get("status", "UNKNOWN"),
            PROPERTY_STATUS_VALUES,
            "property_transaction.status",
        )

    return result


async def triage_email(email: EmailForTriage) -> TriageResponse:
    """
    Ollama-only triage.

    If Ollama fails, returns invalid JSON, or returns invalid enum values,
    the exception is allowed to bubble up to the API route.
    No fallback triage is used.
    """
    result = await generate_json_from_ollama(build_triage_prompt(email))
    result = _normalize_ollama_result(result)

    return TriageResponse(**result)