import mock

from cloudplayer.api.access import Available, Empty, Fields


def test_fields_should_be_eager_with_values_and_lazy_with_targets():
    fields = Fields('one', 'two', 'six')
    assert fields._target is None
    assert fields._values == {'one', 'two', 'six'}
    target = object()
    assert fields is fields(target)
    assert fields._target is target
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


def test_available_fields_init_eagerly_and_extract_fields_from_target():
    target = mock.Mock()
    target.__fields__ = ['ten', 'six', 'two']
    f1 = Available(target)
    assert f1._target is target
    assert set(f1) == {'ten', 'six', 'two'}
    f2 = Available(target)(target)
    assert f2._target is target
    assert set(f2) == {'ten', 'six', 'two'}


def test_fields_module_exposes_empty_fields_object():
    assert len(list(Empty)) == 0
    assert not Empty._target
    assert not Empty._values
