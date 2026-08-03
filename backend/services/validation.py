from dataclasses import dataclass


@dataclass(frozen=True)
class CredentialInput:
    title: str
    website: str
    username: str
    password: str


def validate_credential_input(credential_input: CredentialInput) -> dict[str, bool]:
    return {
        "title": bool(credential_input.title.strip()),
        "website": bool(credential_input.website.strip()),
        "username": bool(credential_input.username.strip()),
        "password": bool(credential_input.password),
    }
