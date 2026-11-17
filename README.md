# RuleScript

**RuleScript is an open language for validating and transforming data.** Its specification defines the grammar and execution semantics for `.rules` files. RuleGenius is developing a RuleScript engine for its CLI and API.

Status: **0.1 draft**. This repository contains the RuleScript specification, interface designs, examples and syntax checks. The RuleGenius engine, CLI and public API are planned. The specification is licensed under [Apache 2.0](LICENSE).

## A readable rule

```text
rule "Valid price":
  check price is required
  check price is a number
  check price is between 0 and 10000
  message "Enter a numeric price from 0 to 10000"
```

- One instruction per line; no semicolons.
- Named `rule` blocks with two-space indentation.
- Plain field names such as `price`; exact headers with spaces use backticks: `` `Unit Price` ``.
- Double quotes for text; expressions such as `price * quantity` are unquoted.
- `check` validates, `set` assigns, `when` guards a rule, `message` explains a failure.

## Read the draft

- [Language and execution semantics](docs/specification.md)
- [Concrete EBNF grammar](grammar/rulespec.ebnf)
- [One CLI and one API execution interface](docs/execution.md)
- [Preview each rule before execution](docs/preview.md)
- [Masking and removal of identifying fields](docs/privacy.md)
- [Canonical bilingual reference catalogue](reference/catalog.json)
- [Complete supplier rules](examples/supplier_product_feed_v1.rules), [input CSV](examples/supplier-input.csv), [expected output CSV](examples/supplier-output.csv)
- [Syntax checks and conformance scenarios](tests/README.md)

## Preview the plan first

Planned source-only interface:

```sh
rulegenius supplier_product_feed_v1.rules --preview
```

See the ordered rules, conditions, field changes and messages before supplying data. The same API endpoint accepts `mode=preview`. Preview does not inspect a dataset or prove that its checks will pass; execution is a separate request. [Read the complete contract](docs/preview.md).

## Execute the complete file

Planned RuleGenius interface:

```sh
rulegenius supplier_product_feed_v1.rules supplier-input.csv --output output.csv --report report.json
```

The same file can mix transformations and checks. The CLI and `POST /v1/executions` apply the whole file in order using RuleScript; they do not select separate transform/validate dialects.

The current examples use flat CSV records or a JSON array of flat records. Dataset-wide checks and additional data formats are outside this core draft.

## Contribute

Discuss language changes and examples in the [RuleScript issue tracker](https://github.com/rulegenius-labs/rulescript/issues). Implementations must follow the specified grammar and semantics. The [pilot runtime conformance suite](tests/README.md#runtime-conformance) checks a subset of that behavior against an implementation.

Run documentation and syntax checks with Python 3:

```sh
python3 tools/check_examples.py
```
