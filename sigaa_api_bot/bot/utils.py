import logging


def pretty_print_model(model: dict) -> str:
    """Convert a Pydantic model into a human-readable string."""

    def format_model(name, value) -> None:
        if isinstance(value, dict):
            lines.append(f"*{name.capitalize().replace('_', ' ')}*:")
            for sub_field, sub_value in value.items():
                lines.append(
                    f"  - *{sub_field.capitalize().replace('_', ' ')}*: {sub_value}"
                )
        else:
            lines.append(f"*{name.capitalize().replace('_', ' ')}*: {value}")

    lines = []
    if isinstance(model, list):
        for field in model:
            for field_name, field_value in field.items():
                format_model(field_name, field_value)
    if isinstance(model, dict):
        for key, item in model.items():
            format_model(key, item)

    return "\n".join(lines)


def enable_logging() -> logging.Logger:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    return logging.getLogger(__name__)
