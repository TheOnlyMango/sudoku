#!/usr/bin/env python3
"""Test script for security features."""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chat.config.security import (
    TokenManager, RateLimiter, validate_file_upload,
    sanitize_filename, MAX_FILE_SIZE
)


def test_token_manager():
    """Test token-based authentication."""
    print("Testing Token Manager...")

    tm = TokenManager()

    # Generate token
    token1 = tm.generate_token("alice")
    print(f"  ✓ Generated token for alice: {token1[:16]}...")

    # Verify token
    valid, username = tm.verify_token(token1)
    assert valid and username == "alice", "Token verification failed"
    print(f"  ✓ Token verified for {username}")

    # Generate new token (should invalidate old one)
    token2 = tm.generate_token("alice")
    assert token1 != token2, "New token should be different"
    print(f"  ✓ New token generated: {token2[:16]}...")

    # Old token should be invalid
    valid, _ = tm.verify_token(token1)
    assert not valid, "Old token should be invalid"
    print("  ✓ Old token correctly invalidated")

    # Invalid token
    valid, _ = tm.verify_token("invalid_token")
    assert not valid, "Invalid token should not verify"
    print("  ✓ Invalid token rejected")

    print("✓ Token Manager: ALL TESTS PASSED\n")


def test_rate_limiter():
    """Test rate limiting."""
    print("Testing Rate Limiter...")

    rl = RateLimiter()

    # Send messages within limit
    for i in range(10):
        allowed, msg = rl.check_message_rate("bob")
        assert allowed, f"Message {i+1} should be allowed"
    print("  ✓ 10 messages allowed within limit")

    # Exceed limit
    allowed, msg = rl.check_message_rate("bob")
    assert not allowed, "Message 11 should be blocked"
    print(f"  ✓ Message 11 blocked: {msg}")

    # Different user should have separate limit
    allowed, _ = rl.check_file_rate("charlie")
    assert allowed, "Different user should have own limit"
    print("  ✓ Different users have separate limits")

    print("✓ Rate Limiter: ALL TESTS PASSED\n")


def test_file_validation():
    """Test file upload validation."""
    print("Testing File Upload Validation...")

    # Valid PDF
    pdf_data = b'%PDF-1.4\n%Fake PDF content'
    valid, msg = validate_file_upload("test.pdf", pdf_data)
    assert valid, "Valid PDF should be accepted"
    print("  ✓ Valid PDF accepted")

    # Invalid PDF (wrong magic bytes)
    fake_pdf = b'This is not a PDF'
    valid, msg = validate_file_upload("test.pdf", fake_pdf)
    assert not valid, "Fake PDF should be rejected"
    print(f"  ✓ Fake PDF rejected: {msg}")

    # File too large
    large_data = b'x' * (MAX_FILE_SIZE + 1)
    valid, msg = validate_file_upload("large.txt", large_data)
    assert not valid, "Oversized file should be rejected"
    print(f"  ✓ Oversized file rejected: {msg}")

    # Invalid extension
    valid, msg = validate_file_upload("malware.exe", b'MZ\x90\x00')
    assert not valid, "Disallowed file type should be rejected"
    print(f"  ✓ Disallowed extension rejected: {msg}")

    # Valid PNG
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
    valid, msg = validate_file_upload("image.png", png_data)
    assert valid, "Valid PNG should be accepted"
    print("  ✓ Valid PNG accepted")

    print("✓ File Validation: ALL TESTS PASSED\n")


def test_filename_sanitization():
    """Test filename sanitization."""
    print("Testing Filename Sanitization...")

    # Directory traversal
    safe = sanitize_filename("../../etc/passwd")
    assert safe == "passwd", f"Got: {safe}"
    print(f"  ✓ Directory traversal blocked: '../../etc/passwd' → '{safe}'")

    # Dangerous characters
    safe = sanitize_filename("file<>:|?*.txt")
    assert '<' not in safe and '>' not in safe, "Dangerous chars should be removed"
    print(f"  ✓ Dangerous characters removed: 'file<>:|?*.txt' → '{safe}'")

    # Long filename
    long_name = "a" * 200 + ".txt"
    safe = sanitize_filename(long_name)
    assert len(safe) <= 104, f"Filename too long: {len(safe)}"  # 100 + ".txt"
    print(f"  ✓ Long filename truncated: {len(long_name)} → {len(safe)} chars")

    # Normal filename
    safe = sanitize_filename("my_file-2024.pdf")
    assert safe == "my_file-2024.pdf", "Normal filename should be unchanged"
    print(f"  ✓ Normal filename preserved: '{safe}'")

    print("✓ Filename Sanitization: ALL TESTS PASSED\n")


def test_database_pool():
    """Test database connection pooling."""
    print("Testing Database Connection Pool...")

    from db_pool import get_pool
    import tempfile
    import os

    # Create temporary database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)

    try:
        pool = get_pool(db_path, pool_size=3)

        # Test connection acquisition
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
            cursor.execute("INSERT INTO test (value) VALUES ('hello')")
        print("  ✓ Connection acquired and table created")

        # Test multiple concurrent connections
        connections_used = 0
        with pool.get_connection() as conn1:
            connections_used += 1
            with pool.get_connection() as conn2:
                connections_used += 1
                cursor = conn2.cursor()
                cursor.execute("SELECT value FROM test WHERE id = 1")
                result = cursor.fetchone()
                assert result[0] == 'hello', "Data should persist"
        print(f"  ✓ {connections_used} concurrent connections successful")

        # Test automatic commit
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM test")
            count = cursor.fetchone()[0]
            assert count == 1, "Auto-commit should work"
        print("  ✓ Automatic commit works")

        # Cleanup
        pool.close_all()
        print("  ✓ Pool closed successfully")

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

    print("✓ Database Pool: ALL TESTS PASSED\n")


def main():
    """Run all security feature tests."""
    print("=" * 60)
    print("  SECURITY FEATURES TEST SUITE")
    print("=" * 60)
    print()

    tests = [
        test_token_manager,
        test_rate_limiter,
        test_file_validation,
        test_filename_sanitization,
        test_database_pool,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}\n")
            failed += 1

    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
