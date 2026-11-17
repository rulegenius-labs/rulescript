# One execution model, two transports

The RuleScript specification defines the language and execution semantics. RuleGenius plans to use one RuleScript engine for the CLI and API interfaces described here.

## CLI

```sh
rulegenius supplier.rules input.csv --output output.csv --report report.json
```

One executable reads one `.rules` file and one data file, then applies every rule in order. The rule contents determine checks and transformations. No subcommand or separate compile step is required. In execute mode, `--output` is required and `--report` is optional. Source-only `--preview` omits the data file and rejects `--output`; see [Preview before execution](preview.md). The output must have the same data format as the input and must not resolve to either source file. CSV and JSON are the core formats.

Exit codes: `0` for a completed passing execution, `1` for a completed failed execution, `2` for usage, syntax, unsupported-format or I/O errors. Commit output atomically only on success; do not create or replace output data on failure. Reports are UTF-8 JSON and may be written on either completed result. Argument validation rejects report/output paths that overlap each other or the input files.

## API

One endpoint: **`POST /v1/executions`**, `multipart/form-data` with:

| Part | Content |
| --- | --- |
| `rules` | UTF-8 `.rules` file; required in both modes |
| `mode` | `execute` (default) or `preview` |
| `data` | CSV/JSON records; required in execute mode, omitted in preview mode |

```sh
curl -X POST https://api.rulegenius.com/v1/executions \
  -F 'rules=@supplier.rules' \
  -F 'data=@input.csv'
```

This hostname illustrates the proposed request; no public API is announced. A single JSON record is supplied as a one-element JSON array using the same endpoint. There are no per-file-name routes or separate validation/transformation endpoints.

In execute mode, HTTP `200` means execution completed; inspect `status`, which is `passed` or `failed`. Malformed rules/data, missing parts and invalid options return `400` before execution; unsupported input format returns `415`. A deployment must document size limits and return `413` before processing an oversized request. An internal service failure returns `500` with no data output.

Passing execute response shape (the source hash is the hash of the canonical supplier example):

```json
{"spec_version":"0.1-draft","mode":"execute","rules_sha256":"9a656bf2a4780801c731dc6fe48e121c1f33e57656538b1d167d0683e0df687b","status":"passed","summary":{"input_records":2,"output_records":2,"filtered_records":0,"failed_records":0},"failures":[],"output":{"format":"csv","content":"price,quantity,country,total\n25,2,US,50\n10.5,3,CA,31.5\n"}}
```

Failing completed response shape:

```json
{"spec_version":"0.1-draft","mode":"execute","rules_sha256":"9a656bf2a4780801c731dc6fe48e121c1f33e57656538b1d167d0683e0df687b","status":"failed","summary":{"input_records":2,"output_records":0,"filtered_records":0,"failed_records":1},"failures":[{"rule":"Valid price","record":2,"code":"CHECK_FAILED","message":"Enter a numeric price from 0 to 10000"}],"output":null}
```

The CLI report has the same `spec_version`, `mode`, `rules_sha256`, `status`, `summary` and `failures` properties, with no embedded `output` content because the data is written to `--output`. `failed_records` counts distinct records with any failure; `filtered_records` counts records removed by a filter that have not failed; `output_records` is zero when execution fails. A failure may include a generic code such as `TRANSFORM_FAILED` or `EXPRESSION_FAILED`, without raw field contents. HTTP `200` and CLI exit `1` can describe the same completed failing run; transport status and rule outcome are separate.

Large or asynchronous execution, authentication, quotas and stored rule registries are future service concerns and do not introduce another DSL or execution endpoint in this core draft.

## Preview mode

Use `rulegenius supplier.rules --preview` or send `rules` and `mode=preview` to the same `POST /v1/executions` endpoint. Supply no data or output path. A source-only plan explains each rule's guard, steps, field effects and failure message; it does not evaluate records. HTTP `200` with `status: "ready"` / CLI exit `0` means only that the plan was generated. `executed` and `data_inspected` remain false and `output` is null. See the [complete preview contract and examples](preview.md).
