import pytest

from comb_spec_searcher.utils import CompressedStringDict


class TestCompressedStringDict:
    @pytest.fixture
    def d(self):
        d = CompressedStringDict([("a", "b"), (2, "c")])
        return d

    def test_get(self, d):
        assert d["a"] == "b"
        assert d[2] == "c"
        assert d.get(1) is None
        assert d.get(2) == "c"

    def test_set(self, d):
        d[3] = "12"
        d["a"] = "aa"
        assert d[3] == "12"
        assert d["a"] == "aa"
