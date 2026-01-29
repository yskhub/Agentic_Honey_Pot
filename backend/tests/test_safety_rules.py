from backend.safety.safety_rules import check_reply_safety, sanitize_reply


def test_block_financial_instruction():
    text = "Please send Rs. 5000 to my account"
    res = check_reply_safety(text)
    assert res["allowed"] is False
    assert res["reason"] == "financial_instruction"


def test_block_upi_with_instruction():
    text = "My UPI id is abc@upi. Please pay now"
    res = check_reply_safety(text)
    assert res["allowed"] is False
    assert res["reason"].startswith("identifier") or res["reason"] == "upi_with_instruction"


def test_redact_digits():
    text = "The account number is 123456789012"
    res = check_reply_safety(text)
    assert res["allowed"] is True
    assert res["reason"] == "redacted_digits"
    assert "XXXX" in res["sanitized"] or res["sanitized"].count('X') >= 8


def test_sanitize_reply_keeps_last4():
    out = sanitize_reply("acct 9876543210")
    assert out.endswith("3210")
