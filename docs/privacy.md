# Mask and anonymize

RuleSpec 0.1 distinguishes a presentation replacement from explicit removal of identifying fields.

```text
rule "Mask email":
  mask email with "****@domain.com"

rule "Remove identifying fields":
  anonymize email, phone, `Full Name`
```

`mask` replaces a field with the supplied constant. It does not search for PII or establish that a dataset is anonymous.

`anonymize` is a privacy-intent operation that removes every explicitly named field from the working records, the output schema and serialized data. Missing/duplicate target fields fail the affected record so a misspelled name is not silently ignored. Run it after checks/calculations that need those fields. The original input file is never modified. Reports and diagnostics must not echo record values at any stage, including failures before removal.

This is a bounded PII-removal capability, not automatic discovery of all PII or a guarantee of irreversible dataset anonymization. Indirect identifiers, combinations of attributes, free text and external data can still permit identification. There is no hashing/pseudonymization shortcut or arbitrary Python/JavaScript evaluation in this operation. Automatic PII detection and anonymization profiles require a separate design and validation step.

For a public release, assess remaining fields and re-identification risk for the actual dataset and use case. The distinction between direct identifiers and quasi-identifiers follows [NIST SP 800-188](https://csrc.nist.gov/pubs/sp/800/188/final).
