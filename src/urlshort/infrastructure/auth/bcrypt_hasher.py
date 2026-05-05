from __future__ import annotations

import bcrypt

_BCRYPT_MAX_BYTES = 72


def _to_bytes(s: str) -> bytes:
    return s.encode("utf-8")[:_BCRYPT_MAX_BYTES]


class BcryptHasher:
    def __init__(self, *, rounds: int = 12) -> None:
        self._rounds = rounds

    def hash(self, plain: str) -> str:
        salt = bcrypt.gensalt(rounds=self._rounds)
        return bcrypt.hashpw(_to_bytes(plain), salt).decode("utf-8")

    def verify(self, plain: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(_to_bytes(plain), hashed.encode("utf-8"))
        except ValueError:
            return False
