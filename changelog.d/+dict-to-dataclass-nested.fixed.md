`dict_to_dataclass` now converts nested config dicts declared as `Optional[X]`, `Union[X, None]`, `List[X]` or a
string annotation (every field of a module using `from __future__ import annotations`) into the dataclass `X`
instead of leaving a plain dict behind, and accepts a value that is already an instance of `X`. (#5201)
