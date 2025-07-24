class UserValidator:
    @staticmethod
    def validate_username(username: str):
        # Validate that username is a non-empty string
        print(f"[VALIDATION] Validating username: {username!r}")
        if not isinstance(username, str) or not username.strip():
            print("[VALIDATION] Validation failed: username must be a non-empty string")
            raise TypeError("Username must be a non-empty string")
        print("[VALIDATION] Username validation passed")