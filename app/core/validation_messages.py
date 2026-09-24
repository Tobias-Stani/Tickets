"""Turns Pydantic/FastAPI validation errors into short Spanish messages."""

FIELD_LABELS = {
    "email": "Email",
    "full_name": "Nombre",
    "password": "Contraseña",
    "role": "Rol",
    "tag_ids": "Etiquetas",
    "name": "Nombre",
    "color": "Color",
    "topic_id": "Tema",
    "subject": "Asunto",
    "description": "Descripción",
    "body": "Respuesta",
    "status": "Estado",
}


def _reason(error: dict) -> str:
    kind, ctx = error.get("type", ""), error.get("ctx") or {}
    reasons = {
        "missing": "es obligatorio",
        "string_too_short": f"debe tener al menos {ctx.get('min_length')} caracteres",
        "string_too_long": f"no puede superar {ctx.get('max_length')} caracteres",
        "string_pattern_mismatch": "tiene un formato inválido",
        "value_error": "no es válido",
    }
    return reasons.get(kind, "tiene un valor inválido")


def describe(errors: list[dict]) -> str:
    parts = []
    for error in errors:
        field = str(error.get("loc", ["campo"])[-1])
        parts.append(f"{FIELD_LABELS.get(field, field)} {_reason(error)}")
    return ". ".join(dict.fromkeys(parts)) + "."
