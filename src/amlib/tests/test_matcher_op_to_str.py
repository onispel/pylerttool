from amlib import model
from amlib import tools

def test_matcher_op_to_str() -> None:
    matcher_equal = model.Matcher(name="foo", value="bar", isEqual=True, isRegex=False)
    assert tools.matcher_op_to_str(matcher_equal) == "="
    matcher_not_equal = model.Matcher(name="foo", value="bar", isEqual=False, isRegex=False)
    assert tools.matcher_op_to_str(matcher_not_equal) == "!="
    matcher_equal_regex = model.Matcher(name="foo", value="bar", isEqual=True, isRegex=True)
    assert tools.matcher_op_to_str(matcher_equal_regex) == "=~"
    matcher_not_equal_regex = model.Matcher(name="foo", value="bar", isEqual=False, isRegex=True)
    assert tools.matcher_op_to_str(matcher_not_equal_regex) == "!~"
    