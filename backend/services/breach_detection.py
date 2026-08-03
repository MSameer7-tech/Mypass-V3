import hashlib
from dataclasses import dataclass
from enum import Enum, auto

import requests


class BreachStatus(Enum):
    SAFE = auto()
    BREACHED = auto()
    OFFLINE = auto()
    ERROR = auto()
    CHECKING = auto()


@dataclass(frozen=True)
class BreachResult:
    breached: bool
    breach_count: int
    status: BreachStatus
    cached: bool = False


class BreachDetectionService:
    """
    Service to securely check if passwords have been exposed in known data breaches
    using the HaveIBeenPwned k-Anonymity API.
    
    Only the first 5 characters of the SHA-1 hash are sent over the network,
    ensuring the full password is never transmitted.
    """
    
    def __init__(self):
        self._cache: dict[str, BreachResult] = {}
        self.timeout_seconds = 3

    def check_password(self, password: str) -> BreachResult:
        """
        Checks a password against HIBP database.
        Uses in-memory cache to avoid redundant API calls.
        """
        if not password:
            return BreachResult(breached=False, breach_count=0, status=BreachStatus.SAFE)
            
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        
        # Check cache
        if sha1_hash in self._cache:
            cached_result = self._cache[sha1_hash]
            return BreachResult(
                breached=cached_result.breached,
                breach_count=cached_result.breach_count,
                status=cached_result.status,
                cached=True
            )

        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]
        
        try:
            response = requests.get(
                f"https://api.pwnedpasswords.com/range/{prefix}",
                headers={"User-Agent": "MyPass-Desktop-App"},
                timeout=self.timeout_seconds
            )
            
            if response.status_code == 200:
                breached = False
                breach_count = 0
                
                # The response contains lines of `hash_suffix:count`
                lines = response.text.splitlines()
                for line in lines:
                    try:
                        line_suffix, count_str = line.split(":")
                        if line_suffix == suffix:
                            breached = True
                            breach_count = int(count_str)
                            break
                    except ValueError:
                        continue
                        
                result = BreachResult(
                    breached=breached,
                    breach_count=breach_count,
                    status=BreachStatus.BREACHED if breached else BreachStatus.SAFE
                )
                self._cache[sha1_hash] = result
                return result
                
            elif response.status_code == 429:
                return BreachResult(breached=False, breach_count=0, status=BreachStatus.ERROR)
            else:
                return BreachResult(breached=False, breach_count=0, status=BreachStatus.ERROR)
                
        except requests.exceptions.RequestException:
            # Catching connection errors, timeouts, offline scenarios
            return BreachResult(breached=False, breach_count=0, status=BreachStatus.OFFLINE)
