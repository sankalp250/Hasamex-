from app.evidence import is_exact_quote_supported


def test_exact_quote_validation():
    source = "The biggest issue is still capital budget approval."
    assert is_exact_quote_supported("The biggest issue is still capital budget approval.", source)
    assert is_exact_quote_supported("The biggest issue is still capital   budget approval.", source)
    assert not is_exact_quote_supported("Hospitals love the technology.", source)
