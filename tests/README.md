# RuleScript checks

Run `python3 tools/check_examples.py` to check the syntax of the canonical catalogue, `.rules` examples and fixtures, and invalid syntax cases. The script also reads the CSV fixtures. It checks source and fixtures without running an engine.

## Runtime conformance

Connect a RuleScript 0.1 draft engine through a command that reads the request below, executes the supplied source and dataset, and translates the result into the response shape. From the repository root, run the following with Python 3.8 or newer. The adapter command can use any language and receives arguments exactly as supplied after `--`.

```sh
python3 tools/check_conformance.py -- python3 /path/to/adapter.py
```

The runner starts one adapter process per case in the current working directory and sends one UTF-8 JSON object on stdin. Each request includes the entire `.rules` source and input dataset. Dataset `format` is `csv` or `json`, and `content` is a string containing the corresponding file contents.

```json
{
  "protocol_version": 1,
  "rules": "rule \"Has price\":\n  check price is required\n",
  "data": {"format": "json", "content": "[{\"price\":0}]"}
}
```

Print exactly one UTF-8 JSON response on stdout. Put adapter logs on stderr. Return process exit code `0` for a completed execution, including executions whose rules give `status: "failed"`. Use a nonzero process exit status to indicate adapter errors.

```json
{
  "protocol_version": 1,
  "status": "passed",
  "summary": {"input_records": 1, "output_records": 1, "filtered_records": 0, "failed_records": 0},
  "failures": [],
  "output": {"format": "json", "content": "[{\"price\":0}]"}
}
```

The response uses the `status`, `summary`, `failures` and `output` fields of the [execution contract](../docs/execution.md). Use `null` output for a failed execution and report each failure with its rule name, original 1-based record index, diagnostic code and message. The runner compares these fields, ignoring the order of failure entries and JSON object members. CSV comparison preserves column order, row order and cell text while allowing equivalent quoting and line endings. JSON numbers and CSV columns declared numeric in a case are compared by decimal value.

The runner allows 10 seconds per case by default. Use `--timeout SECONDS` before `--` to change it. It exits with `0` when every case passes, `1` when any case disagrees or the adapter fails to return a valid response, and `2` for invocation or setup errors.

Add cases in [conformance.json](conformance.json). Each case has a unique `id`, a repo-relative path to the `rules` source, a `data` object, and an `expected` response without `protocol_version`. The case file can supply dataset `content` inline or give a repo-relative `file` path for `data` and `expected.output`. Optional `numeric_columns` names the CSV columns to compare as numbers, allowing equivalent values such as `10.5` and `10.50`.

The starter suite covers ordered CSV transforms, failure without dataset output even if a later rule filters the failed record, and missing/null/empty JSON fields. Its results apply to those cases. Broader conformance would cover all grammar and execution rules, including decimal rounding, aggregates, privacy transformations and transport behavior such as atomic file publication.


## Preview contract fixtures

The same command checks the authored supplier, conditional and privacy preview JSON fixtures against their `.rules` sources: order, names, guards/messages, source lines, source hash, static field effects and explicit non-execution flags. It rejects 11 altered fixtures that claim execution/data inspection, include data output or counts, change a guard into a result, omit instructions/limitations, reorder rules or mismatch source hashes. These are source/contract consistency checks, not tests of a released preview planner or runtime. See [the preview contract](../docs/preview.md).
