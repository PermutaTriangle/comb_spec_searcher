import json

from comb_spec_searcher.strategies import StrategyPack
from example import pack


def test_json_pack():
    npack = StrategyPack.from_dict(json.loads(json.dumps(pack.to_jsonable())))
    assert npack.__class__ == pack.__class__
    assert pack.ver_strats == npack.ver_strats
    assert npack.__dict__ == pack.__dict__
    assert npack == pack
