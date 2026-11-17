# RuleScript tools

Run these commands from the repository root with Python 3.8 or newer. The scripts use the Python standard library.

## Check the examples and preview fixtures

[`check_examples.py`](check_examples.py) checks the syntax of the reference catalogue and `.rules` examples, verifies that the invalid syntax cases are rejected, and reads the supplier CSV fixtures. It also runs the preview fixture checker. Use this command to run the same checks as the repository workflow.

```sh
python3 tools/check_examples.py
```

[`check_preview_contract.py`](check_preview_contract.py) compares the supplier, conditional, and privacy preview fixtures with their `.rules` source, including rule order, source line numbers, and the source hash. It checks that altered fixtures that violate the [preview contract](../docs/preview.md) are rejected. Run it on its own with the following command.

```sh
python3 tools/check_preview_contract.py
```

These two tools check source and fixtures. Use the runtime checker to exercise an engine.

## Check an implementation

[`check_conformance.py`](check_conformance.py) runs the starter execution cases through an engine adapter supplied as a command after `--`. The adapter can use any language. It reads one UTF-8 JSON request from standard input and writes one JSON response to standard output. The runner compares the engine's status, record counts, diagnostics, and output against the expected values for each case.

```sh
python3 tools/check_conformance.py -- python3 /path/to/adapter.py
```

The runner reports pass or fail per case. The [adapter protocol](../tests/README.md#runtime-conformance) specifies the payloads, exit codes, timeout, and how to add cases. The [language specification](../docs/specification.md) defines the behavior an engine implements.
