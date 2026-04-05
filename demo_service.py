# demo_service.py

"""
Demo Service: Authentication Retry Logic

This simulates a real backend service where login requests
may fail due to network issues.
"""

import time


class AuthService:
    def __init__(self):
        # ❌ BUG: Too low retry count causes frequent failures
        self.max_retries = 1
        self.timeout = 2  # seconds

    def authenticate(self, user_id):
        """
        Simulates authentication with retry logic
        """
        attempts = 0

        while attempts < self.max_retries:
            try:
                return self._call_auth_service(user_id)
            except TimeoutError as e:
                print(f"[Attempt {attempts+1}] Timeout occurred")
                attempts += 1
                time.sleep(1)

        # ❌ ISSUE: Fails too quickly due to low retries
        raise Exception("Authentication failed after retries")

    def _call_auth_service(self, user_id):
        """
        Simulates an external API call that fails intermittently
        """
        # Simulate failure
        raise TimeoutError("Auth service timeout")


if __name__ == "__main__":
    service = AuthService()

    try:
        service.authenticate("user_123")
    except Exception as e:
        print("Final Error:", str(e))