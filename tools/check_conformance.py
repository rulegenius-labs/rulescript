#!/usr/bin/env python3
"""Run RuleScript execution cases against an external engine adapter."""

import argparse
import csv
import io
import json
import math
import subprocess
import sys
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_VERSION = 1


def read_source(path):
    return (ROOT / path).read_bytes().decode("utf-8")


def inline_dataset(dataset):
    if "file" in dataset:
        return {"format": dataset["format"], "content": read_source(dataset["file"])}
    return dataset


def read_cases():
    cases = json.loads(read_source("tests/conformance.json"))
    if not cases or len({case["id"] for case in cases}) != len(cases):
        raise ValueError("Expected a nonempty suite with unique case IDs")
    for case in cases:
        case["rules"] = read_source(case["rules"])
        case["data"] = inline_dataset(case["data"])
        expected = case["expected"]
        if expected["output"] is not None:
            expected["output"] = inline_dataset(expected["output"])
    return cases


def reject_constant(value):
    raise ValueError(f"Nonfinite number in JSON: {value}")


def distinguish_booleans(value):
    # Python considers True equal to 1 and False equal to 0.
    if isinstance(value, bool):
        return ("boolean", value)
    if isinstance(value, list):
        return [distinguish_booleans(item) for item in value]
    if isinstance(value, dict):
        return {key: distinguish_booleans(item) for key, item in value.items()}
    return value


def csv_number(text):
    try:
        number = Decimal(text)
    except InvalidOperation as error:
        raise ValueError(f"Expected a numeric CSV cell, got {text!r}") from error
    if not number.is_finite():
        raise ValueError(f"Expected a finite numeric CSV cell, got {text!r}")
    return number


def comparable_output(output, numeric_columns):
    if output is None:
        return None
    if not isinstance(output, dict) or set(output) != {"format", "content"}:
        raise ValueError("output must be null or contain exactly 'format' and 'content'")
    content = output["content"]
    if not isinstance(content, str):
        raise ValueError("output.content must be a string")
    if output["format"] == "csv":
        rows = list(csv.reader(io.StringIO(content, newline=""), strict=True))
        if numeric_columns:
            if not rows:
                raise ValueError("CSV output requires a header")
            header, *records = rows
            indices = {header.index(name) for name in numeric_columns}
            rows = [header] + [
                [csv_number(value) if index in indices else value for index, value in enumerate(record)]
                for record in records
            ]
        return "csv", rows
    if output["format"] == "json":
        records = json.loads(content, parse_float=Decimal, parse_int=Decimal, parse_constant=reject_constant)
        return "json", distinguish_booleans(records)
    raise ValueError(f"Unexpected output format {output['format']!r}")


def differences(response, expected, numeric_columns):
    if not isinstance(response, dict):
        raise ValueError("Expected a JSON object on standard output")
    version = response.get("protocol_version")
    if type(version) is not int or version != PROTOCOL_VERSION:
        raise ValueError(f"Expected protocol_version {PROTOCOL_VERSION}, got {version!r}")
    result = {key: value for key, value in response.items() if key != "protocol_version"}
    if result.keys() != expected.keys():
        raise ValueError(f"Expected result fields {sorted(expected)}, got {sorted(result)}")

    for key, expected_value in expected.items():
        actual_value = result[key]
        if key == "output":
            matches = comparable_output(expected_value, numeric_columns) == comparable_output(actual_value, numeric_columns)
        elif key == "failures":
            if not isinstance(actual_value, list):
                raise ValueError("failures must be an array")
            expected_items = Counter(json.dumps(item, sort_keys=True) for item in expected_value)
            actual_items = Counter(json.dumps(item, sort_keys=True) for item in actual_value)
            matches = expected_items == actual_items
        else:
            matches = distinguish_booleans(expected_value) == distinguish_booleans(actual_value)
        if not matches:
            yield f"{key}: expected {expected_value!r}, got {actual_value!r}"


def run_case(case, command, timeout):
    request = {"protocol_version": PROTOCOL_VERSION, "rules": case["rules"], "data": case["data"]}
    process = subprocess.run(
        command,
        input=(json.dumps(request, ensure_ascii=False) + "\n").encode("utf-8"),
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    if process.returncode:
        detail = process.stderr.decode("utf-8", errors="replace").strip()[:500]
        raise ValueError(f"Adapter exited with code {process.returncode}" + (f": {detail}" if detail else ""))
    response = json.loads(process.stdout.decode("utf-8"), parse_constant=reject_constant)
    return list(differences(response, case["expected"], case.get("numeric_columns", [])))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=10, help="Seconds allowed per case (default: 10)")
    parser.add_argument("adapter", nargs=argparse.REMAINDER, help="-- followed by the adapter command and arguments")
    args = parser.parse_args()
    if len(args.adapter) < 2 or args.adapter[0] != "--":
        parser.error("provide an adapter command after --")
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be a positive finite number")

    try:
        cases = read_cases()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Cannot load conformance cases: {error}", file=sys.stderr)
        return 2

    passed = 0
    for case in cases:
        try:
            mismatches = run_case(case, args.adapter[1:], args.timeout)
        except OSError as error:
            print(f"Cannot launch adapter: {error}", file=sys.stderr)
            return 2
        except subprocess.TimeoutExpired:
            mismatches = [f"Adapter timed out after {args.timeout:g} seconds"]
        except (ValueError, csv.Error) as error:
            mismatches = [f"Invalid adapter response: {error}"]

        if mismatches:
            print(f"FAIL {case['id']}", file=sys.stderr)
            for mismatch in mismatches:
                print(f"  {mismatch}", file=sys.stderr)
        else:
            print(f"PASS {case['id']}")
            passed += 1

    print(f"{passed}/{len(cases)} RuleScript execution cases passed (starter suite).")
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
