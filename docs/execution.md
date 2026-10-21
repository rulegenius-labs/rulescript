# One execution model, two transports

RuleSpec defines the DSL and execution semantics. RuleScript implements them for RuleGenius. The CLI/API below are planned interfaces, not released software or live endpoints.

## CLI

```sh
rulegenius supplier.rules input.csv --output output.csv --report report.json
```

One executable reads one `.rules` file and one data file, then applies every rule in order. The rule contents determine checks and transformations. No subcommand or separate compile step is required. `--output` is required; `--report` is optional. The output must have the same data format as the input and must not resolve to either source file. CSV and JSON are the core formats.

Exit codes: `0` for a completed passing execution, `1` for a completed failed execution, `2` for usage, syntax, unsupported-format or I/O errors. Commit output atomically only on success; do not create or replace output data on failure. Reports are UTF-8 JSON and may be written on either completed result. Argument validation rejects report/output paths that overlap each other or the input files.

## API

One endpoint: **`POST /v1/executions`**, `multipart/form-data` with:

| Part | Content |
| --- | --- |
| `rules` | UTF-8 `.rules` file |
| `data` | `.csv` file or `.json` file containing an array of records |

```sh
curl -X POST https://api.rulegenius.com/v1/executions \
  -F 'rules=@supplier.rules' \
  -F 'data=@input.csv'
```

This hostname illustrates the proposed request; no public API is announced. A single JSON record is supplied as a one-element JSON array using the same endpoint. There are no per-file-name routes or separate validation/transformation endpoints.

HTTP `200` means execution completed; inspect `status`, which is `passed` or `failed`. Malformed rules/data, missing parts and invalid options return `400` before execution; unsupported input format returns `415`. A deployment must document size limits and return `413` before processing an oversized request. An internal service failure returns `500` with no data output.

Passing response shape:

```json
{"spec_version":"0.1-draft","status":"passed","summary":{"input_records":2,"output_records":2,"filtered_records":0,"failed_records":0},"failures":[],"output":{"format":"csv","content":"price,quantity,country,total\n25,2,US,50\n10.5,3,CA,31.5\n"}}
```

Failing completed response shape:

```json
{"spec_version":"0.1-draft","status":"failed","summary":{"input_records":2,"output_records":0,"filtered_records":0,"failed_records":1},"failures":[{"rule":"Valid price","record":2,"code":"CHECK_FAILED","message":"Enter a numeric price from 0 to 10000"}],"output":null}
```

The CLI report has the same `spec_version`, `status`, `summary` and `failures` properties, with no embedded `output` content because the data is written to `--output`. `failed_records` counts distinct records with any failure; `filtered_records` counts records removed by a filter that have not failed; `output_records` is zero when execution fails. A failure may include a generic code such as `TRANSFORM_FAILED` or `EXPRESSION_FAILED`, without raw field contents. HTTP `200` and CLI exit `1` can describe the same completed failing run; transport status and rule outcome are separate.

Large or asynchronous execution, authentication, quotas and stored rule registries are future service concerns and do not introduce another DSL or execution endpoint in this core draft.
