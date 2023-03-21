from amlib import model
from amlib import tools
import re

def test_is_matching() -> None:

    matecher_eq = model.Matcher(name="match_eq", value="value1", isEqual=True, isRegex=False)
    assert tools.is_matching("value1", matecher_eq) == True
    assert tools.is_matching("value2", matecher_eq) == False
    matcher_neq = model.Matcher(name="match_neq", value="value2", isEqual=False, isRegex=False)
    assert tools.is_matching("value2", matcher_neq) == False
    assert tools.is_matching("value1", matcher_neq) == True
    matcher_eq_re = model.Matcher(name="match_eq_re", value="f.o", isEqual=True, isRegex=True)
    assert tools.is_matching("foo", matcher_eq_re) == True
    assert tools.is_matching("bar", matcher_eq_re) == False
    matcher_neq_re = model.Matcher(name="match_neq_re", value="f.o", isEqual=False, isRegex=True)
    assert tools.is_matching("foo", matcher_neq_re) == False
    assert tools.is_matching("bar", matcher_neq_re) == True