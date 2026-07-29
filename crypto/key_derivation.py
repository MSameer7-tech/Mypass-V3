import base64
import json
import os
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ArgonParameters:
    iterations: int = 3
    lanes: int = 4
    memory_cost: int = 65536
    length: int = 32
    salt_length: int = 16


class Argon2KeyDerivationService:
    def default_parameters(self) -> ArgonParameters:
        return ArgonParameters()

    def generate_salt(self, length: int) -> bytes:
        return os.urandom(length)

    def derive_key(self, master_password: str, salt: bytes, parameters: ArgonParameters) -> bytes:
        from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

        kdf = Argon2id(
            salt=salt,
            length=parameters.length,
            iterations=parameters.iterations,
            lanes=parameters.lanes,
            memory_cost=parameters.memory_cost,
        )
        # AES-256-GCM requires exactly 32 raw bytes, not a base64-encoded representation.
        return kdf.derive(master_password.encode())

    def derive_legacy_fernet_key(
        self,
        master_password: str,
        salt: bytes,
        parameters: ArgonParameters,
    ) -> bytes:
        return base64.urlsafe_b64encode(self.derive_key(master_password, salt, parameters))

    def serialize_parameters(self, parameters: ArgonParameters) -> str:
        return json.dumps(asdict(parameters))

    def deserialize_parameters(self, raw_parameters: str) -> ArgonParameters:
        if not raw_parameters:
            return self.default_parameters()
        data = json.loads(raw_parameters)
        return ArgonParameters(**data)

    def encode_salt(self, salt: bytes) -> str:
        return base64.b64encode(salt).decode()

    def decode_salt(self, encoded_salt: str) -> bytes:
        return base64.b64decode(encoded_salt.encode())
