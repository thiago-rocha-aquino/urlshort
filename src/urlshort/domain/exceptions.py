from __future__ import annotations


class DomainError(Exception):
    """Erro de regra de negocio do dominio."""


class EntityNotFoundError(DomainError):
    def __init__(self, entity: str, identifier: object) -> None:
        super().__init__(f"{entity} nao encontrado: {identifier!r}")
        self.entity = entity
        self.identifier = identifier


class DuplicateEntityError(DomainError):
    def __init__(self, entity: str, field: str, value: object) -> None:
        super().__init__(f"{entity} duplicado em {field}={value!r}")
        self.entity = entity
        self.field = field
        self.value = value


class InvalidCredentialsError(DomainError):
    def __init__(self) -> None:
        super().__init__("credenciais invalidas")


class SlugAlreadyTakenError(DomainError):
    def __init__(self, slug: str) -> None:
        super().__init__(f"slug ja em uso: {slug!r}")
        self.slug = slug


class UrlExpiredError(DomainError):
    def __init__(self) -> None:
        super().__init__("URL expirada")


class UrlMaxClicksReachedError(DomainError):
    def __init__(self) -> None:
        super().__init__("limite de cliques atingido")


class WrongPasswordError(DomainError):
    def __init__(self) -> None:
        super().__init__("senha incorreta")


class ForbiddenError(DomainError):
    def __init__(self, message: str = "acesso negado") -> None:
        super().__init__(message)
