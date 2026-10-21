# Preview before execution

RuleSpec defines a source-only preview plan for the same RuleScript engine, CLI and API. This is a planned interface contract; no runtime preview command or public API is released yet. The DSL grammar is unchanged.

## CLI

```sh
rulegenius supplier.rules --preview
rulegenius supplier.rules --preview --report plan.json
```

Use the same executable with `--preview`. Supply only the `.rules` source; no data file or `--output` is accepted in preview mode. Invalid combinations are usage errors (exit `2`). Parse and inspect the source, then print a human-readable explanation to stdout. Optional `--report` writes the same machine-readable JSON plan as the API, atomically. The report path must not resolve to the rules source. Source files are never modified and no transformed data file is created or replaced.

Exit `0` means a syntactically valid plan was generated, possibly with limitations/warnings. Exit `2` means usage, source syntax/static structure or I/O error. Exit `1` is reserved for completed failing executions and is not used for preview. A ready plan does not mean any data check passed.

Human-readable example for the [supplier file](../examples/supplier_product_feed_v1.rules):

```text
Preview only — no data inspected or rules executed

1. Prepare supplier data
   Rename `Unit Price` to price
   Convert price to number and quantity to integer
   Set total to price * quantity

2. Valid price
   Require price, check its number type and inclusive range 0–10000
   On check failure: "Enter a numeric price from 0 to 10000"

3. Supported country
   Check that country is US, CA or MX
   On check failure: "Country must be US, CA or MX"

Actual field availability, values and row outcomes remain unknown.
```

After reviewing it, execution is a separate explicit invocation:

```sh
rulegenius supplier.rules input.csv --output output.csv --report report.json
```

Preview never executes automatically afterwards. Each mode reads the current source file afresh; the plan is not an executable artifact, saved authorization or a promise about changed files.

## API

Keep **`POST /v1/executions`** with multipart form data:

```sh
curl -X POST https://api.rulegenius.com/v1/executions \
  -F 'rules=@supplier.rules' \
  -F 'mode=preview'
```

The hostname illustrates the planned interface. `rules` is required in both modes. `mode` accepts `execute` (default) or `preview`; an unknown mode is `400`. `data` is required for execution and must be omitted for preview; unexpected data in preview is rejected with `400`, not silently inspected or executed. Preview does not accept an output filename. It returns JSON with HTTP `200` only when the source can be planned, `mode: "preview"`, `status: "ready"`, `executed: false`, `data_inspected: false` and `output: null`.

Malformed source or invalid form parts return `400`, unsupported source encoding/format `415`, documented size-limit violations `413`, and internal errors `500`. Errors do not fall back to execution and must not claim a ready plan. Execution continues to use `passed`/`failed` outcomes; a preview never returns either outcome.

## What a plan explains

Return rule blocks and their steps in exact file order. For each rule include its name, optional `when` condition (source text, unevaluated), optional `message` and ordered instructions. Each instruction includes its line number, operation, original instruction text, exact field names it reads/writes/removes and a plain-language explanation. Explain checks, assignments/conversions, filters, masks and identifying-field removal. Conditional steps are described as conditional, never as already selected, skipped or completed.

The plan may explain statically known dependencies, including a field created by an earlier step and used by a later step, plus operations that would overwrite or remove output fields. It cannot establish whether input fields actually exist or whether a destination would collide with an input field. `writes` lists destinations that may be assigned/created; `removes` lists fields that would cease to exist, including the source name of a rename. These lists describe intent on a matching record, not observed changes. Source literals may appear in explanations; record values must never appear. Escape control characters when rendering source names/literals to terminal text.

Every plan includes `DATA_NOT_INSPECTED`. Additional warnings describe source-visible effects or unresolved requirements; warnings have stable `code`, nullable `rule` and human-readable `message` properties. The fixtures include a warning for explicit identifying-field removal. Explanatory prose may be localized; clients must use the structured operations and fields, not parse the prose.

## Shared JSON contract

The CLI `--report` file and successful API preview response have the same shape:

| Property | Meaning |
| --- | --- |
| `spec_version` | `0.1-draft` |
| `mode`, `status` | `preview`, `ready` |
| `executed`, `data_inspected` | Both `false` |
| `rules_sha256` | Lowercase SHA-256 of the exact uploaded/read UTF-8 source bytes, including line endings; identifies this source snapshot. |
| `output` | Always `null`; a plan report is not data output. |
| `plan.rules` | Ordered rules with `order`, `name`, `when`, `message`, `steps`. |
| `steps` | `order`, `line`, `operation`, `source`, `reads`, `writes`, `removes`, `explanation`. Field arrays contain unique names in code-point order. |
| `plan.warnings` | Stable codes and explanatory messages; includes the source-only limitation. |

Rule and step orders are one-based. `line` is the one-based source line. Guard/message metadata do not become executable steps. Execution reports also include `mode: "execute"` and `rules_sha256`, allowing comparison with a previous preview, without making preview mandatory or automatically authorizing execution.

The [supplier plan](../examples/supplier-preview.json), [conditional plan](../examples/conditional-preview.json) and [privacy plan](../examples/privacy-preview.json) are canonical illustrative response fixtures. They are authored contract examples, not results from an implemented engine. They are checked against their source files and shared with the website. No data was supplied when preparing these fixtures.

## Boundaries

Preview parses source syntax/static structure and builds an explanation. It must not read a dataset, run transformations or checks, evaluate arithmetic, evaluate guards or filters, calculate aggregates, test anonymization, or execute even a subset of rows. It must not report record counts, matched conditions, validation success, predicted data samples, estimated affected rows or runtime success.

Whether actual values can be converted, which branches match, what aggregates return, how many records pass/get filtered, and whether data is de-identified remain unknown until a separate execution and any needed privacy assessment. If the source changes, generate a new plan and compare the source hash. Preview is not a dry run, runtime verification or a dataset anonymity claim.
