# Draft checks

Run `python3 tools/check_examples.py`. The dependency-free syntax checker accepts the canonical catalogue and every `.rules` example, rejects the negative syntax fixtures, and checks CSV fixtures are readable. It does not execute transformations/checks, parse the EBNF automatically, or establish runtime compliance.

The expected supplier output is an execution fixture for future implementations, not a result produced by the checker. Runtime conformance must additionally cover required zero/false/null/blank values; inclusive bounds; backtick escaping and exact headers; guard short-circuiting; decimal rounding; immutable aggregate snapshots; filtered-vs-failed outcomes; anonymize removing all named fields; no raw values in reports; CSV column consistency; and identical CLI/API results.
