from amlib import model
from amlib import tools

def test_parse_matcher() -> None:
    testexpr1 = "foo=bar"
    testexpr2 = "foo!=bar"
    testexpr3 = "foo=~bar"
    testexpr4 = "foo!=~bar"

    matcher1 = tools.parse_matcher(testexpr1)
    assert matcher1 is not None
    assert matcher1.name == "foo"
    assert matcher1.value == "bar"
    assert matcher1.isEqual == True
    assert matcher1.isRegex == False
    matcher2 = tools.parse_matcher(testexpr2)
    assert matcher2 is not None
    assert matcher2.name == "foo"
    assert matcher2.value == "bar"
    assert matcher2.isEqual == False
    assert matcher2.isRegex == False
    matcher3 = tools.parse_matcher(testexpr3)
    assert matcher3 is not None
    assert matcher3.name == "foo"
    assert matcher3.value == "bar"
    assert matcher3.isEqual == True
    assert matcher3.isRegex == True
    matcher4 = tools.parse_matcher(testexpr4)
    assert matcher4 is not None
    assert matcher4.name == "foo"
    assert matcher4.value == "bar"
    assert matcher4.isEqual == False
    assert matcher4.isRegex == True
