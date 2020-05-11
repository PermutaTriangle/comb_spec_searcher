from comb_spec_searcher.strategies.strategy import (
    AtomStrategy,
    EmptyStrategy,
    strategy_from_dict,
)


def test_json_encoding():
    atom = AtomStrategy()
    new_atom = strategy_from_dict(atom.to_jsonable())
    assert atom.__class__ == new_atom.__class__
    assert atom.__dict__ == new_atom.__dict__
    empty = EmptyStrategy()
    new_empty = strategy_from_dict(empty.to_jsonable())
    assert empty.__class__ == new_empty.__class__
    assert empty.__dict__ == new_empty.__dict__


def test_equality():
    atom1 = AtomStrategy()
    atom2 = AtomStrategy()
    assert atom1 == atom2
