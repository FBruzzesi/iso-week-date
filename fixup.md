# Second-iteration backlog: remaining P2 / P3 findings

Follow-up to the correctness pass that fixed the five P1 findings. Every item below was
**re-reproduced against the post-P1 tree**, and every line number is current as of that tree.

---

## ⚠️ Read this before planning from this file

**This is not a complete review.** The `/ce-code-review` run that produced these findings dispatched
**one of six** selected reviewers before work was redirected to the P1 fixes. Only the
**correctness** reviewer ran. These never ran:

| Reviewer | What it would have looked for | Why it was selected |
|---|---|---|
| `api-contract` | Public signatures, semver breakage, the frozen surface | Published PyPI package at v2.3.0 |
| `adversarial` | Green-while-red validation, composition failures, abuse cases | Validation is a silent-pass mechanism |
| `testing` | Vacuous assertions, brittle coupling, untested branches | `tests/` was explicitly in scope |
| `maintainability` | The two 1000+ line files, structural traps | `isoweek.py` 1209 lines, `isoweekdate.py` 1098 |
| `performance` | Vectorised transforms, generator paths | pandas/polars transforms |

For a project about to freeze, **`api-contract` and `maintainability` are the two most valuable
lenses and neither has run**. Consider completing the review before committing to this backlog:

```text
/ce-code-review depth:full
```

Sections 1–3 below are the correctness reviewer's own output. Section 4 is my own reading of the
code, which has **not** been through an independent reviewer or the confidence/evidence gate — treat
it as leads, not findings.

---

## 1. Findings (correctness reviewer, P2/P3, unaddressed)

| # | Sev | Item | Location |
|---|-----|------|----------|
| [F1](#f1) | P2 | polars checks return `Expr`, not the documented `bool` | `polars_utils.py:277,309,332` |
| [F2](#f2) | P3 | `weekday` guard accepts non-`int` lookalikes | `pandas_utils.py:179`, `polars_utils.py:219` |
| [F3](#f3) | P3 | `daysout` errors name the wrong parameter | `isoweekdate.py:1065,1069` |
| [F4](#f4) | P3 | `IsoWeekDate.to_compact` docstring has the wrong format | `isoweekdate.py:532` |

> Note: line numbers in `_base.py` / `isoweekdate.py` shifted slightly after the `from_date`
> zero-padding fix landed in this PR. Re-grep if an offset looks off by a few lines.

### F1

**P2 — polars checks return an `Expr` while annotated and documented as `bool`.**

`src/iso_week_date/polars_utils.py:277` (`_match_series`), `:309` (`is_isoweek_series`), `:332`
(`is_isoweekdate_series`), and the namespace methods at `:557` / `:573`.

Reproduced:

```python
type(is_isoweek_series(pl.col("a")))  # Expr, not bool
bool(
    is_isoweek_series(pl.col("a"))
)  # TypeError: the truth value of an Expr is ambiguous
```

`Expr.all()` returns an `Expr`, so the `# type: ignore[return-value]` at `:304` is silencing a real
mismatch. A caller who trusts the annotation and writes `if is_isoweek_series(expr):` gets a
`TypeError` at runtime. The `except Exception: return False` guard also cannot fire for an `Expr`,
since nothing is evaluated eagerly.

**Fix — keep `Expr` support and type it honestly (recommended).** Overloads give exact per-input
types instead of a union every caller must narrow:

```python
@overload
def is_isoweek_series(series: pl.Series) -> bool:
    ...


@overload
def is_isoweek_series(series: pl.Expr) -> pl.Expr:
    ...


def is_isoweek_series(series: ExprOrSeries) -> bool | pl.Expr:
    return _match_series(series, ISOWEEK_PATTERN.pattern)
```

Apply the same shape to `is_isoweekdate_series` and `SeriesIsoWeek.is_isoweek` / `.is_isoweekdate`;
annotate `_match_series` as `-> bool | pl.Expr` and drop the `type: ignore`. Document that an `Expr`
input yields a boolean `Expr` for use inside `select` / `filter`, and that the `except` fallback is
eager-only.

The alternative (reject `Expr`, keep `-> bool`) is **breaking** for anyone already passing an
expression, and loses genuinely useful functionality. Don't.

**Test:** `is_isoweek_series(pl.col("a"))` inside `df.select(...)` for matching, non-matching and
null-bearing frames; assert the returned type for both input kinds.
**Semver:** minor — annotations and docs only, no runtime change.

### F2

**P3 — `weekday` is validated with `not in range(1, 8)`, which accepts anything `int`-comparable.**

`src/iso_week_date/pandas_utils.py:179` and `src/iso_week_date/polars_utils.py:219`. The same class
of hole exists in `isoweek.py` `to_datetime` (`:545`) and `nth` (`:1029`), which check
`isinstance(..., int)` but do not exclude `bool`.

Reproduced — each produces a cryptic downstream parse error instead of a clear `TypeError`:

```python
pandas_utils.isoweek_to_datetime(pd.Series(["2023-W01"]), weekday=1.0)
# ValueError: unconverted data remains when parsing with format ...
pandas_utils.isoweek_to_datetime(pd.Series(["2023-W01"]), weekday=True)
# ValueError: time data "2023-W01-True" doesn't match format ...
polars_utils.isoweek_to_datetime(pl.Series(["2023-W01"]), weekday=1.0)
# InvalidOperationError: conversion from `str` to `date` failed
IsoWeek("2023-W01").to_datetime(True)
# ValueError: time data '2023-W01-True' does not match format '%G-W%V-%u'
```

`True` slips through because `isinstance(True, int)` is `True` **and** `True in range(1, 8)` is
`True` (it equals `1`); the value is then interpolated as the literal string `"True"`.

**Fix.** Add the type check the docstrings already promise, in both frame-utils modules before the
range check:

```python
if not isinstance(weekday, int) or isinstance(weekday, bool):
    msg = f"`weekday` must be an integer between 1 and 7, found {type(weekday)}"
    raise TypeError(msg)
if weekday not in range(1, 8):
    ...
```

Add the `isinstance(..., bool)` exclusion to `isoweek.py:545` (`weekday`) and `:1029` (`n`) too.

**Test:** parametrise `1.0`, `True`, `False`, `"1"`, `Decimal(1)` over both backends and both scalar
methods; assert `TypeError` with the documented message.
**Semver:** patch for the frame utils (a confusing error becomes a clear one). Rejecting `bool` is
technically breaking, but only swaps one exception for a better one — no working call changes.

### F3

**P3 — `daysout` error messages name `n_weeks` instead of `n_days`.**

`src/iso_week_date/isoweekdate.py:1065` and `:1069`. Reproduced:

```python
IsoWeekDate("2023-W01-1").daysout(
    0
)  # ValueError: `n_weeks` must be strictly positive, found 0
IsoWeekDate("2023-W01-1").daysout(
    1.0
)  # TypeError: `n_weeks` must be integer, found <class 'float'>
```

Copy-paste from `IsoWeek.weeksout`. A user grepping their own call sites for `n_weeks` finds nothing.

**Fix.** `:1065` -> ``f"`n_days` must be integer, found {type(n_days)} type"``; `:1069` ->
``f"`n_days` must be strictly positive, found {n_days}"``. Check
`tests/isoweekdate/daysout_test.py` for a `pytest.raises(match=...)` on the old wording.
**Semver:** patch.

### F4

**P3 — `IsoWeekDate.to_compact` docstring states the wrong format.**

`src/iso_week_date/isoweekdate.py:532` says `YYYYWNN`; the method returns `YYYYWNND`, as its own
doctest two lines below and `from_compact` at `:409` both show.

**Fix.** One-line docstring correction. **Semver:** patch, docs only.

---

## 2. Residual risks (correctness reviewer — real behaviour, not filed as findings)

These were verified but deliberately not filed, mostly because the behaviour is arguably correct or
documented-by-omission. Each needs a **decide-then-document-or-fix** call.

### R1 — Year-bound arithmetic raises undocumented low-level errors

Reproduced at the documented `0001`–`9999` bounds:

```python
IsoWeek("9999-W52").next()  # OverflowError: date value out of range
IsoWeek("0001-W01").previous()  # OverflowError: date value out of range
IsoWeek("9999-W52").days  # ValueError: year must be in 1..9999, not 10000
IsoWeekDate("9999-W52-7").next()  # ValueError: year must be in 1..9999, not 10000
```

Unavoidable given the `datetime.date` backing, but no `Raises:` section mentions it, and
`OverflowError` leaks the implementation.

**Recommended:** document in the `Raises:` sections of `__add__`/`__sub__`/`next`/`previous`/`days`/
`nth`/`to_date`/`to_datetime`, and add tests pinning current behaviour (covers **T2** below).
Optionally raise a domain error instead, but that adds a bounds check to every arithmetic call for a
range almost nobody reaches — probably not worth it.

### R2 — `range()` is start-anchored, so `end` is dropped when the span isn't a multiple of `step`

Reproduced, `W01`..`W05` with `step=2`:

| `inclusive` | Result |
|---|---|
| `both` | `('2025-W01', '2025-W03', '2025-W05')` |
| `left` | `('2025-W01', '2025-W03')` |
| `right` | `('2025-W02', '2025-W04')` |
| `neither` | `('2025-W02', '2025-W04')` |

`inclusive="right"` yielding **neither** endpoint is the surprising one. This matches builtin
`range` and `pd.date_range` conventions, so it is defensible.

**Recommended:** don't change the behaviour; add a worked `step=2` example to the `range` docstring
covering all four `inclusive` values, so it is discoverable rather than surprising.

### R3 — Same-offset subclass comparison raises `TypeError` in both directions

```python
class Custom(IsoWeek):
    pass  # same offset_ as IsoWeek


IsoWeek("2023-W01") < Custom(
    "2023-W02"
)  # TypeError: Cannot compare `Custom` with type ...
Custom("2023-W01") < IsoWeek("2023-W02")  # TypeError (same message)
IsoWeek("2023-W01") == Custom("2023-W01")  # False — does not raise
```

Two causes compounding, in `_base.py`:

1. The guard is `isinstance(other, self.__class__)` (`:115`, `:129`), so the subclass instance
   rejects its own parent.
2. `__gt__` is `not self.__le__(other)` and `__ge__` is `not self.__lt__(other)` (`:143`, `:146`).
   Python's reflected-operand rule runs the *subclass's* `__gt__` first, which negates a `__le__`
   that raises — so both directions fail with the subclass named.

That `==` returns `False` while `<` raises is the inconsistency worth resolving.

**Fix (most invasive item here — sequence it deliberately).** Introduce one shared guard and stop
defining `__gt__`/`__ge__` as negations:

```python
def _comparable(self: Self, other: object) -> bool:
    return (
        isinstance(other, BaseIsoWeek)
        and self._pattern is other._pattern  # same granularity: IsoWeek vs IsoWeekDate
        and self.offset_ == other.offset_
    )
```

then implement all four operators directly against `self.value_` using that guard. Keeps the
"different offsets cannot be compared" rule, and makes subclasses interoperate with their base.
**Semver:** minor (previously-raising calls start working). **Alternative:** document the limitation
and pin it with a test — cheaper, and reasonable if the freeze is close.

### R4 — `contains` and `__contains__` disagree for subclasses

```python
class Custom(IsoWeek):
    pass


Custom("2023-W01").contains(IsoWeek("2023-W01"))  # TypeError
IsoWeek("2023-W01").contains(Custom("2023-W01"))  # True
```

`__contains__` guards on `self.__class__` (`isoweek.py:1140`) while `contains` guards on the
hardcoded `IsoWeek` (`:1180`). Fix alongside **R3** with the same `_comparable`-style predicate so
one rule governs equality, ordering and containment. **Semver:** minor.

### R5 — pandas null semantics verified on one version only

The `_match_series` null handling (`pandas_utils.py:265`) locates nulls via `series.notna()`
specifically because under the pandas 3.0 `str` dtype `str.fullmatch` collapses nulls to `False`
before they can be inspected. Verified across `object` / `str` / `string` dtypes on **pandas 3.0.5
only**. The declared floor is now `>=1.1.0`, and this is exactly the area where pandas' NA handling
has shifted historically.

**Recommended:** add a CI job resolving the lowest direct versions, e.g.
`uv run --resolution lowest-direct --all-extras --group tests pytest tests/frame_utils`, so the
declared floor is actually exercised.

---

## 3. Test gaps (correctness reviewer, unaddressed)

| # | Gap | Notes |
|---|-----|-------|
| T1 | No `pl.Expr` coverage for `is_isoweek_series` / `is_isoweekdate_series` | Why **F1** went unnoticed. Fix with F1. |
| T2 | No tests at the documented `0001`/`9999` year bounds under arithmetic | Fix with **R1**. |
| T3 | No non-`int` `weekday` cases (`1.0`, `True`) in either backend | Fix with **F2**. |

Already closed by the P1 pass: one-shot iterators, trailing whitespace, pydantic `ValidationError`
for non-`str`, null parametrisation in both backends, and cross-backend parity
(`tests/frame_utils/parity_test.py`).

---

## 4. Additional leads (my own reading — NOT independently reviewed)

No confidence/evidence gate was applied to these. Verify before acting.

### O1 — `_compact_pattern` is dead code carrying `# pragma: no cover`

`_base.py:149`. **Zero usages** in `src/`, `tests/` or `docs/` — `from_compact` uses
`_compact_format`, not `_compact_pattern`. The `# pragma: no cover` at `:153` hides that it is never
executed.

Note: it is *not* a performance problem. `re.compile` caches internally, so repeated access returns
the same object — I initially assumed otherwise and was wrong.

**Options:** delete it (cleanest; `_`-prefixed and the class docstring calls the semiprivate
attributes "do not use directly", but it is still reachable by users — so a major-version change), or
keep it, add a test, and drop the pragma. Decide before the freeze; dead code with a coverage
exemption is the worst of the three states.

### O2 — Uncovered `offset` guard in `pandas_utils.isoweekdate_to_datetime`

Lines `225-226`, the only uncovered lines in `src/` (96% on that file). The sibling
`isoweek_to_datetime` has the identical guard *and* a test. One parametrise case closes it:
`isoweekdate_to_datetime(pd.Series(["2023-W01-1"]), offset="abc")` -> `TypeError`.

### O3 — Bare `except Exception` in polars `_match_series`

`polars_utils.py:305`. Swallows everything to `False`, so a genuine bug reads as "not ISO week
format". Narrow to the observed failure modes (`InvalidOperationError`, `SchemaError`,
`ComputeError`). Related: it cannot fire at all for an `Expr` (see **F1**).

### O4 — The checks validate format, not the calendar

`is_isoweek_series(["2023-W53"])` is `True`, but `IsoWeek("2023-W53")` raises — 2023 has only 52
weeks. **Already documented** in this PR (a warning admonition in
`docs/user-guide/dataframe-modules.md`, pinned by
`test_is_isoweek_series_is_a_format_check_not_a_calendar_check`). Listed so iteration 2 can decide
whether to *close* it rather than document it: that needs a vectorised `weeks_of_year` in both
backends (feasible — it is pure integer arithmetic over the year column).

### O5 — `bool` is accepted wherever `int` is

`IsoWeek("2025-W01") + True` returns `2025-W02`. Harmless-ish and idiomatic Python, but combined with
**F2** it produces the `"2023-W01-True"` class of error. Worth one decision covering both.

### O7 — `pandas_utils.datetime_to_isoweek` ISO-year padding is unverified below year 1677

`pandas_utils.py:70` still formats via `Series.dt.strftime(_format)`, which delegates to
`datetime.strftime` and therefore to the platform C library — the exact dependency that caused
`from_date` to emit `"1-W01"` on glibc with Python < 3.14 (fixed in the scalar path by
`BaseIsoWeek._format_isocalendar`). `polars_utils.py:64` also uses `dt.strftime`, but polars formats
through Rust chrono and is covered by
`tests/frame_utils/polars_test.py::test_datetime_to_isoweek_zero_pads_the_iso_year`.

There is **no pandas equivalent test**, because `datetime64[ns]` cannot represent a year before
1677, and the non-nanosecond units that can require pandas >= 2.0 — above the declared `>=1.1.0`
floor. So the exposure is narrow (it needs pandas >= 2.0 *and* a non-ns dtype *and* a pre-1000 date)
but it is genuinely unverified.

**Options:** add a test guarded on `pandas >= 2.0` using `dtype="datetime64[us]"`; or format from
`series.dt.isocalendar()` (a DataFrame of `year`/`week`/`day`) instead of `strftime`, mirroring the
scalar fix. Pair the decision with **R5** (the lowest-direct-resolution CI job).

### O6 — polars `_match_series` returns `False` for `Categorical` / `Enum` dtypes

`pl.Series(["2024-W01"], dtype=pl.Categorical).str.contains(...)` raises `InvalidOperationError`,
which **O3**'s bare `except` converts to `False` — a wrong answer for a valid column.
Fix: `.cast(pl.String)` when the dtype is `Categorical`/`Enum`, or document the limitation.

---

## Suggested sequencing

1. **Pure wins, no design decisions** — F3, F4, O2, T1/T3 (with F2). Small, safe, patch-level.
2. **Type-contract correctness** — F1 (+T1), F2 (+T3), O3, O6. Mostly annotations and guards.
3. **Decide-then-act** — R1 (+T2), R2, O1, O4, O5, O7. Each is a document-or-fix call, not a bug.
4. **Behavioural, breaking-ish — do last or defer past the freeze** — R3 + R4 together (one
   shared comparability predicate), R5 (CI matrix).

Before starting, strongly consider running the five reviewers that never ran, especially
`api-contract` and `maintainability` — a maintenance freeze makes public-surface and structural
findings the expensive class to miss.
