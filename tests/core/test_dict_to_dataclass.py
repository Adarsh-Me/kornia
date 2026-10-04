from dataclasses import dataclass, field
from typing import List, Optional, Union

import pytest

from kornia.core.exceptions import TypeCheckError
from kornia.core.utils import dict_to_dataclass


@dataclass
class Inner:
    a: int = 0


@dataclass
class Plain:
    inner: Inner = field(default_factory=Inner)


@dataclass
class Wrapped:
    inner: Inner = field(default_factory=Inner)
    maybe: Optional[Inner] = None
    either: Union[Inner, None] = None
    many: List[Inner] = field(default_factory=list)
    quoted: "Inner" = field(default_factory=Inner)


def test_plain_annotation_still_converts():
    out = dict_to_dataclass({"inner": {"a": 1}}, Plain)
    assert isinstance(out.inner, Inner)
    assert out.inner.a == 1


def test_optional_union_list_and_quoted_annotations_convert():
    payload = {
        "inner": {"a": 1},
        "maybe": {"a": 2},
        "either": {"a": 3},
        "many": [{"a": 4}, {"a": 5}],
        "quoted": {"a": 6},
    }
    out = dict_to_dataclass(payload, Wrapped)
    assert [getattr(out, name).a for name in ("inner", "maybe", "either", "quoted")] == [1, 2, 3, 6]
    assert [type(getattr(out, name)).__name__ for name in ("maybe", "either", "quoted")] == ["Inner"] * 3
    assert [type(x).__name__ for x in out.many] == ["Inner", "Inner"]
    assert [x.a for x in out.many] == [4, 5]


def test_absent_and_none_values_are_left_alone():
    out = dict_to_dataclass({"inner": {"a": 1}, "maybe": None, "many": []}, Wrapped)
    assert out.maybe is None
    assert out.many == []
    assert isinstance(out.inner, Inner)


def test_already_converted_instances_are_accepted():
    out = dict_to_dataclass({"inner": Inner(7), "maybe": Inner(8), "many": [Inner(9)]}, Wrapped)
    assert (out.inner.a, out.maybe.a, out.many[0].a) == (7, 8, 9)


def test_non_dataclass_fields_keep_their_values():
    @dataclass
    class Scalars:
        n: int = 0
        s: str = ""
        flag: bool = False
        opt: Optional[int] = None
        raw: dict = field(default_factory=dict)

    out = dict_to_dataclass({"n": 3, "s": "x", "flag": True, "opt": None, "raw": {"k": 1}}, Scalars)
    assert (out.n, out.s, out.flag, out.opt) == (3, "x", True, None)
    assert out.raw == {"k": 1}
    assert type(out.raw) is dict


def test_non_dict_input_still_rejected():
    with pytest.raises(TypeCheckError, match="Input conf must be dict"):
        dict_to_dataclass([{"a": 1}], Plain)
