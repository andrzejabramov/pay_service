class NotFoundError(Exception):
    """Исключение для случаев, когда сущность не найдена."""

    def __init__(self, entity: str, identifier: str):
        self.entity = entity
        self.identifier = identifier
        super().__init__(f"{entity} with identifier '{identifier}' not found")


class ValidationError(Exception):
    """Исключение для ошибок бизнес-валидации."""

    def __init__(self, field: str, value: str, message: str):
        self.field = field
        self.value = value
        self.message = message
        super().__init__(message)
