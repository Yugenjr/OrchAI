from orchai.policy.scope import ScopeComparator

def test_scope_comparator_compliant():
    expected = ["src/**", "tests/**"]
    actual = ["src/main.py", "tests/test_main.py", "src/auth/login.py"]
    
    result = ScopeComparator.compare(expected, actual)
    assert result.compliant is True
    assert len(result.unexpected_changes) == 0

def test_scope_comparator_unexpected():
    expected = ["src/**"]
    actual = ["src/main.py", "README.md", "package.json"]
    
    result = ScopeComparator.compare(expected, actual)
    assert result.compliant is False
    assert "README.md" in result.unexpected_changes
    assert "package.json" in result.unexpected_changes
    assert "src/main.py" not in result.unexpected_changes

def test_scope_comparator_path_normalization():
    # Test windows style backslashes
    expected = ["src/**"]
    actual = ["src\\auth\\login.py"]
    
    result = ScopeComparator.compare(expected, actual)
    assert result.compliant is True
