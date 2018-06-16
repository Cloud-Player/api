from unittest import mock

from cloudplayer.api.access import Available, Fields


def test_fields_should_be_eager_with_values_and_lazy_with_targets():
    fields = Fields('one', 'two', 'six')
    assert fields._target is None
    assert fields._values == {'one', 'two', 'six'}
    target = object()
    assert fields in fields(target)
    assert fields(target)._target is target
    assert set(fields) == {'one', 'two', 'six'}


def test_fields_should_check_field_containment_against_values():
    fields = Fields('one', 'two', 'six')
    assert 'one' in fields
    assert 'zero' not in fields
    f1 = Fields('one', 'five')
    assert f1 not in fields
    f2 = Fields('one', 'two', 'six', 'nine')
    assert f2 not in fields
    f3 = Fields('one', 'six')
    assert f3 in fields


def test_available_fields_init_eagerly_and_keep_empty_values():
    target = mock.Mock()
    f1 = Available(target)
    assert f1._target is target
    assert len(list(f1)) == 0
    f2 = Available(target)(target)
    assert f2._target is target
    assert len(list(f2)) == 0


def test_available_fields_are_always_contained_in_specific_fields():
    target = mock.Mock()
    f1 = Available(target)
    f2 = Fields('ten', 'six', 'two')
    assert f1 in f2
    f1 = Available(target)
    f2 = Fields()
    assert f1 in f2
