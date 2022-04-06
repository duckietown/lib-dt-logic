from dt_logic.validation import safe_chained_dict_get


def test_safe_chained_get():
    d = {'a': {'b': {'c': 1}}}
    assert safe_chained_dict_get(d, "a", "b", "c") == 1
    assert safe_chained_dict_get(d, "a", "c") is None
    assert safe_chained_dict_get(d, "b") is None
