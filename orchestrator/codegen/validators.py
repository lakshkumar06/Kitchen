import json
from pydantic import ValidationError
from ..models import AppSpec

def validate_spec(text_or_obj):
    try:
        obj = json.loads(text_or_obj) if isinstance(text_or_obj, str) else text_or_obj
        AppSpec.model_validate(obj)
        return obj
    except (ValidationError, json.JSONDecodeError):
        return None
