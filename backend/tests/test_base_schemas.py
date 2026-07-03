from app.base_schemas import serialise_relationships


class DummyObject:
    """Simple dummy object with an ID attribute for testing."""

    def __init__(self, id_: int) -> None:
        self.id = id_


class TestSerialiseRelationships:
    """Tests for serialise_relationships utility function."""

    def test_empty_list(self) -> None:
        """An empty list should return an empty list."""
        assert serialise_relationships([]) == []

    def test_simple_list(self) -> None:
        """A list of integers should be returned unchanged."""
        assert serialise_relationships([2, 1]) == [2, 1]

    def test_entry_list(self) -> None:
        """A list of objects should be serialised to their IDs."""
        objects = [DummyObject(1), DummyObject(3), DummyObject(2)]
        assert serialise_relationships(objects) == [1, 3, 2]
