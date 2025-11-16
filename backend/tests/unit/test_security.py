"""
Unit tests for security module (password hashing, JWT tokens).
Constitution Principle VI: Test-Driven Phase Completion
Target: ≥90% coverage per T022b requirement
"""
import pytest
import time
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException

from src.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_token,
    validate_token,
    TokenData,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from src.core.config import settings


class TestPasswordHashing:
    """Test password hashing and verification."""

    @pytest.mark.unit
    @pytest.mark.auth
    def test_hash_password_creates_bcrypt_hash(self):
        """Test that password hashing creates a valid bcrypt hash."""
        password = "SecurePassword123!"
        hashed = hash_password(password)

        # Bcrypt hashes start with $2b$
        assert hashed.startswith("$2b$")
        assert len(hashed) == 60  # Bcrypt hash length
        assert hashed != password  # Hash should differ from plaintext

    @pytest.mark.unit
    @pytest.mark.auth
    def test_hash_password_different_each_time(self):
        """Test that hashing same password produces different hashes (salt)."""
        password = "SecurePassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2  # Different salts

    @pytest.mark.unit
    @pytest.mark.auth
    def test_verify_password_correct_password(self):
        """Test that correct password verification succeeds."""
        password = "SecurePassword123!"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    @pytest.mark.unit
    @pytest.mark.auth
    def test_verify_password_incorrect_password(self):
        """Test that incorrect password verification fails."""
        password = "SecurePassword123!"
        wrong_password = "WrongPassword456!"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    @pytest.mark.unit
    @pytest.mark.auth
    def test_verify_password_empty_password(self):
        """Test that empty password verification fails."""
        password = "SecurePassword123!"
        hashed = hash_password(password)

        assert verify_password("", hashed) is False


class TestJWTTokens:
    """Test JWT token creation and decoding."""

    @pytest.mark.unit
    @pytest.mark.auth
    def test_create_access_token_valid_structure(self):
        """Test that access token has valid JWT structure."""
        user_id = "test-user-123"
        email = "test@example.com"

        token = create_access_token(user_id=user_id, email=email)

        assert isinstance(token, str)
        assert len(token.split(".")) == 3  # JWT has 3 parts

    @pytest.mark.unit
    @pytest.mark.auth
    def test_create_access_token_contains_claims(self):
        """Test that access token contains required claims."""
        user_id = "test-user-123"
        email = "test@example.com"

        token = create_access_token(user_id=user_id, email=email)
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        assert payload["user_id"] == user_id
        assert payload["email"] == email
        assert "exp" in payload  # Expiration time

    @pytest.mark.unit
    @pytest.mark.auth
    def test_create_refresh_token_valid_structure(self):
        """Test that refresh token has valid JWT structure."""
        user_id = "test-user-123"

        token = create_refresh_token(user_id=user_id)

        assert isinstance(token, str)
        assert len(token.split(".")) == 3

    @pytest.mark.unit
    @pytest.mark.auth
    def test_decode_token_valid_token(self):
        """Test decoding a valid token."""
        user_id = "test-user-123"
        email = "test@example.com"

        token = create_access_token(user_id=user_id, email=email)
        payload = decode_token(token)

        assert payload is not None
        assert payload["user_id"] == user_id
        assert payload["email"] == email

    @pytest.mark.unit
    @pytest.mark.auth
    def test_decode_token_invalid_token(self):
        """Test decoding an invalid token returns None."""
        invalid_token = "invalid.token.here"

        payload = decode_token(invalid_token)

        assert payload is None

    @pytest.mark.unit
    @pytest.mark.auth
    @pytest.mark.skip(reason="Token expiration has clock skew tolerance - tested in integration")
    def test_decode_token_expired_token(self):
        """Test decoding an expired token returns None."""
        import time
        user_id = "test-user-123"
        email = "test@example.com"

        # Create token with very short expiration
        token = create_access_token(
            user_id=user_id,
            email=email,
            expires_delta=timedelta(milliseconds=1)
        )

        # Wait for token to expire
        time.sleep(0.01)

        payload = decode_token(token)

        assert payload is None

    @pytest.mark.unit
    @pytest.mark.auth
    def test_token_custom_expiration(self):
        """Test creating token with custom expiration."""
        user_id = "test-user-123"
        email = "test@example.com"
        custom_delta = timedelta(hours=1)

        token = create_access_token(
            user_id=user_id,
            email=email,
            expires_delta=custom_delta
        )

        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        assert "exp" in payload


class TestTokenValidation:
    """Test JWT token validation with validate_token function."""

    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_token_valid_access_token(self):
        """Test validating a valid access token."""
        user_id = "valid-user-123"
        email = "valid@example.com"

        token = generate_token(user_id, email, token_type="access")
        token_data = validate_token(token, expected_type="access")

        assert isinstance(token_data, TokenData)
        assert token_data.user_id == user_id
        assert token_data.email == email
        assert token_data.token_type == "access"
        assert isinstance(token_data.exp, datetime)

    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_token_valid_refresh_token(self):
        """Test validating a valid refresh token."""
        user_id = "refresh-user-123"
        email = "refresh@example.com"

        token = generate_token(user_id, email, token_type="refresh")
        token_data = validate_token(token, expected_type="refresh")

        assert token_data.user_id == user_id
        assert token_data.token_type == "refresh"

    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_token_wrong_type(self):
        """Test that validating token with wrong expected type fails."""
        user_id = "wrong-type-123"
        email = "wrong@example.com"

        # Create access token but validate as refresh
        token = generate_token(user_id, email, token_type="access")

        with pytest.raises(HTTPException) as exc_info:
            validate_token(token, expected_type="refresh")

        assert exc_info.value.status_code == 401
        assert "Invalid token type" in exc_info.value.detail

    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_token_invalid_signature(self):
        """Test validating token with invalid signature."""
        user_id = "invalid-sig-123"
        email = "invalid@example.com"

        # Create token with different secret
        bad_token = jwt.encode(
            {"user_id": user_id, "email": email, "token_type": "access",
                "exp": datetime.utcnow() + timedelta(hours=1)},
            "wrong-secret-key",
            algorithm=JWT_ALGORITHM
        )

        with pytest.raises(HTTPException) as exc_info:
            validate_token(bad_token, expected_type="access")

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_token_missing_user_id(self):
        """Test validating token with missing user_id raises 401."""
        bad_token = jwt.encode(
            {"email": "test@example.com", "token_type": "access",
                "exp": datetime.utcnow() + timedelta(hours=1)},
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM
        )

        with pytest.raises(HTTPException) as exc_info:
            validate_token(bad_token, expected_type="access")

        assert exc_info.value.status_code == 401
        assert "Invalid token payload" in exc_info.value.detail

    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_token_missing_email(self):
        """Test validating token with missing email raises 401."""
        bad_token = jwt.encode(
            {"user_id": "user123", "token_type": "access",
                "exp": datetime.utcnow() + timedelta(hours=1)},
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM
        )

        with pytest.raises(HTTPException) as exc_info:
            validate_token(bad_token, expected_type="access")

        assert exc_info.value.status_code == 401
        assert "Invalid token payload" in exc_info.value.detail

    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_token_expired(self):
        """Test validating an expired token raises 401."""
        user_id = "expired-user-123"
        email = "expired@example.com"

        # Create token that expired 1 hour ago
        exp = datetime.utcnow() - timedelta(hours=1)
        expired_token = jwt.encode(
            {
                "user_id": user_id,
                "email": email,
                "token_type": "access",
                "exp": exp,
                "iat": datetime.utcnow() - timedelta(hours=2)
            },
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM
        )

        with pytest.raises(HTTPException) as exc_info:
            validate_token(expired_token, expected_type="access")

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_token_malformed(self):
        """Test validating a malformed token string raises 401."""
        malformed_token = "not.a.valid.jwt.token"

        with pytest.raises(HTTPException) as exc_info:
            validate_token(malformed_token, expected_type="access")

        assert exc_info.value.status_code == 401


class TestGenerateToken:
    """Test generate_token function edge cases."""

    @pytest.mark.unit
    @pytest.mark.auth
    def test_generate_token_invalid_type_raises_value_error(self):
        """Test that invalid token type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid token_type"):
            generate_token("user123", "test@example.com", token_type="invalid")

    @pytest.mark.unit
    @pytest.mark.auth
    def test_access_token_expiration_time_correct(self):
        """Test that access token has correct expiration time (~30 min)."""
        user_id = "expire-test-123"
        email = "expire@example.com"

        before = datetime.utcnow()
        token = generate_token(user_id, email, token_type="access")
        after = datetime.utcnow()

        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        exp_time = datetime.fromtimestamp(payload["exp"])

        # Expiration should be ~30 minutes from now
        expected_min = before + \
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES - 1)
        expected_max = after + \
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES + 1)

        assert expected_min <= exp_time <= expected_max

    @pytest.mark.unit
    @pytest.mark.auth
    def test_refresh_token_expiration_time_correct(self):
        """Test that refresh token has correct expiration time (~7 days)."""
        user_id = "refresh-expire-123"
        email = "refresh-expire@example.com"

        before = datetime.utcnow()
        token = generate_token(user_id, email, token_type="refresh")
        after = datetime.utcnow()

        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        exp_time = datetime.fromtimestamp(payload["exp"])

        # Expiration should be ~7 days from now
        expected_min = before + \
            timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS, hours=-1)
        expected_max = after + \
            timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS, hours=1)

        assert expected_min <= exp_time <= expected_max


class TestPasswordEdgeCases:
    """Test password hashing edge cases."""

    @pytest.mark.unit
    @pytest.mark.auth
    def test_hash_password_case_sensitive(self):
        """Test that password hashing is case-sensitive."""
        password = "CaseSensitive"
        hashed = hash_password(password)

        assert verify_password("CaseSensitive", hashed) is True
        assert verify_password("casesensitive", hashed) is False
        assert verify_password("CASESENSITIVE", hashed) is False

    @pytest.mark.unit
    @pytest.mark.auth
    def test_hash_password_special_characters(self):
        """Test password with special characters."""
        password = "P@ssw0rd!#$%^&*()"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True
        assert verify_password("P@ssw0rd", hashed) is False

    @pytest.mark.unit
    @pytest.mark.auth
    def test_hash_password_unicode_characters(self):
        """Test password with unicode characters."""
        password = "пароль123🔒"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    @pytest.mark.unit
    @pytest.mark.auth
    def test_verify_password_none_values(self):
        """Test password verification edge cases with None/empty."""
        password = "ValidPassword123"
        hashed = hash_password(password)

        # Empty password should fail
        assert verify_password("", hashed) is False


class TestTokenEdgeCases:
    """Test JWT token edge cases."""

    @pytest.mark.unit
    @pytest.mark.auth
    def test_token_with_special_characters_in_email(self):
        """Test token with special characters in email."""
        user_id = "special-123"
        email = "user+tag@sub.example.com"

        token = generate_token(user_id, email, token_type="access")
        token_data = validate_token(token, expected_type="access")

        assert token_data.email == email

    @pytest.mark.unit
    @pytest.mark.auth
    def test_multiple_tokens_for_same_user_are_different(self):
        """Test generating multiple tokens for same user produces different tokens."""
        user_id = "multi-123"
        email = "multi@example.com"

        token1 = generate_token(user_id, email, token_type="access")
        time.sleep(1.1)  # Sleep to ensure different iat timestamp
        token2 = generate_token(user_id, email, token_type="access")

        # Tokens should be different (different iat timestamp)
        assert token1 != token2

        # Both should validate correctly
        data1 = validate_token(token1, expected_type="access")
        data2 = validate_token(token2, expected_type="access")

        assert data1.user_id == data2.user_id == user_id
