# RuleSpec 0.1 — draft language specification

RuleSpec defines the standard DSL. RuleScript is the implementation developed by RuleGenius. The website, CLI and API use this same grammar; implementation-specific alternatives are not separate language dialects.

## Files and rule blocks

UTF-8 source files end in `.rules`. A file contains one or more uniquely named `rule "Name":` blocks. The body is indented exactly two spaces, with one instruction per line. Tabs, semicolons, nested rule blocks and multiline instructions are not part of this draft. Blank lines are allowed. Comments begin with `#` outside quoted strings/fields and end at the newline. Keywords are lowercase and case-sensitive. Rule names are nonempty quoted strings.

An optional `when` is the first body instruction. An optional `message` is last, appears at most once and requires at least one `check`. Between them, checks and transformations execute in their written order. A rule must contain at least one check or transformation. A false guard skips that rule for that record.

## Fields, literals and expressions

- Simple field references match `[A-Za-z_][A-Za-z0-9_]*` and must not be keywords.
- Backticks quote an exact, case-sensitive field name, including spaces, Unicode, punctuation or reserved words: `` `Unit Price` ``, `` `check` ``. A literal backtick is doubled: `` `Cost ``tax`` included` ``. Headers are not trimmed or normalized. Empty/duplicate CSV headers are rejected.
- Double-quoted strings use JSON string escapes. A field reference and a string literal are different: `price` is a field; `"price"` is text.
- Numeric literals are finite decimal numbers with optional fractional and exponent parts. Booleans are `true` and `false`; `null` is explicit absence of a value.
- Arithmetic supports `+ - * /`, unary signs, parentheses and function calls. Multiplication/division bind more tightly than addition/subtraction; operators of equal precedence associate left. Expressions are never put inside strings for evaluation. String content is never executed as code.
- Decimal arithmetic must be consistent across CLI/API. The core numeric context has 34 significant decimal digits and half-even rounding for intermediate arithmetic. Division by zero or nonnumeric operands fails the record. Explicit `round(value, places)` uses decimal half-up (ties away from zero), with places from 0 to 15. Nonfinite values are rejected.

## Conditions

Use `check <condition>`, `when <condition>` or `keep rows where <condition>` with the same condition grammar:

| Form | Meaning |
| --- | --- |
| `field is required` | Present, non-null, not empty or whitespace-only; empty arrays/objects fail. Zero and false pass. |
| `field is missing` / `field is not missing` | Whether the record lacks the key, independent of null. |
| `field is null` / `field is not null` | Explicit null / present non-null. A missing key fails both. |
| `field is a number` / `an integer` / `a string` / `a boolean` / `a date` | Type check without coercion. A date is a valid calendar date in an exact `YYYY-MM-DD` string. |
| `field is between low and high` | Inclusive numeric limits; low must not exceed high. |
| `field is in [values]` / `field is not in [values]` | Exact, case-sensitive membership/exclusion. |
| `field is greater than value` / `field is at least value` | Exclusive / inclusive numeric minimum. |
| `field is less than value` / `field is at most value` | Exclusive / inclusive numeric maximum. |
| `field is value` / `field is not value` | Typed equality/inequality. Integer and number values compare numerically. |

Other predicates on a missing or null operand return false, including negative membership/inequality. Present incompatible operands fail the check; they are not implicitly converted. Non-check expression evaluation errors fail the record. Conditions combine with `and` and `or`, evaluated left to right with short-circuiting; `and` binds more tightly. Parentheses group conditions. The `and` inside `between ... and ...` belongs to that comparison.

Multiple checks in a rule must all pass. The first failed check stops that rule for that record and uses its `message`, if supplied. `message` is literal text, not an expression or data interpolation. A transformation failure produces a generic diagnostic, not a potentially misleading custom validation message. Later rules still execute to collect failures, but failure is permanent for the run.

## Transformations

The [canonical catalogue](../reference/catalog.json) contains complete examples of every core statement.

- `rename source to destination`: require an existing source and a destination that is absent; retain its column position.
- `split source into first, second by "separator"`: require a nonempty literal separator, a string source, absent destination fields and an exact part count; keep the source and append destinations.
- `merge first, second into destination with "separator"`: require string sources and an absent destination; keep sources and append the destination.
- `map field using {"key": value}`: require unique text keys and a string source with an exact match. Unmapped values fail; no implicit fallback.
- `convert field to number / integer / string / boolean / date`: conversion is explicit; missing fields fail, null stays null. Numeric input uses the numeric literal grammar; integer conversion rejects fractions. Boolean conversion accepts only booleans or exact `"true"`/`"false"`. Date conversion requires a valid ISO calendar date. Scalar-to-string conversion uses canonical decimal/boolean/ISO text without locale formatting.
- `set field to expression`: assign or create a field. Referenced missing/null values fail ordinary functions/arithmetic. Plain assignment of the literal null is allowed. Overwriting a field retains its position; new fields append.
- `replace old with new in field`: replace exact typed matches; no match is a no-op, a missing field fails.
- `mask field with "constant"`: replace a present field with a constant string. See [privacy semantics](privacy.md).
- `anonymize field, other`: remove explicitly named identifying fields. See [privacy semantics](privacy.md).
- `drop field, other`: remove existing fields. Duplicate/missing field names fail.
- `fill field with expression`: assign only when the target is missing or null. Empty strings stay unchanged. The replacement expression is evaluated only when needed.
- `reorder columns first, second`: list every retained field exactly once. This defines CSV output order; JSON object member order has no semantic effect.
- `keep rows where condition`: retain only matching rows. An excluded record is filtered, not failed; evaluation errors fail the record. A filter never cancels an earlier failure.

Text functions are `lowercase(text)`, `uppercase(text)`, `titlecase(text)` and `trim(text)`, using Unicode 15.1 default (non-locale-specific) case mappings and White_Space trimming. Titlecase uses Unicode default word boundaries. `round(number, places)` is specified above. Functions reject invalid argument types and arity.

`mean(field)` and `median(field)` are dataset aggregates available only in `fill`. They read an immutable snapshot of currently retained records at the start of the named rule, before its guard/actions. Missing/null cells are ignored; any other nonnumeric cell or an empty numeric population fails the aggregate. Median of an even population is the mean of the two middle values. Aggregates never depend on row iteration order.

## Data adapters and output

The core adapters are CSV and JSON. CSV has a header, comma delimiter, double-quoted escaping and UTF-8 encoding; cells initially remain strings, including empty cells. Convert explicitly before numeric checks. JSON input is an array of flat record objects; scalar types and null are preserved. Nested traversal, implicit field paths, dataset uniqueness constraints and schema metadata directives are outside this draft.

Process rule blocks in file order over a working copy of currently retained records. Capture aggregates before a block begins. Execute each matching record's body in line order. A failed instruction stops that block for that record. Do not mutate either input file. If any record fails, execution is failed and no output data is published, even if a later filter removes that record. A successful output is committed atomically. CSV output must have a consistent column set/order across retained records; incompatible per-record shape changes fail output validation.

Reports use rule names, record indexes (starting at 1), statuses and stable diagnostic codes. Do not include raw record values, removed PII or evaluated expressions containing data. A report can be produced on failure without exposing a partial data output. Empty outputs preserve the known CSV schema; zero records are not an error.

## Interfaces and implementation status

The [CLI/API contract](execution.md) invokes this same execution model for all statements. No separate compile format, transform command or validate command is defined. RuleScript's executable runtime and hosted API have not been released. The repository syntax checker validates source structure; it does not execute rules or certify anonymization.
