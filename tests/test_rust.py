from comb_spec_searcher_rs import sum_as_string


def test_rust_module():
    assert sum_as_string(2, 5) == "7"
