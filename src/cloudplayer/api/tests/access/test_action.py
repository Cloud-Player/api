from cloudplayer.api.access import (Anything, Create, Delete, Query, Read,
                                    Update)


def test_actions_for_extended_crud_are_available_in_module():
    assert Anything()
    assert Create()
    assert Read()
    assert Update()
    assert Delete()
    assert Query()


def test_anything_action_should_equal_anything_else():
    assert Anything() == Anything()
    assert Anything() == Create()
    assert Anything() == object()


def test_operations_should_equal_only_same_action_classes():
    assert Create() == Create()
    assert Create() != Delete()
    assert Create() != object()
