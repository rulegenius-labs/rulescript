# RuleSpec — The Open Standard for Data Validation & Data Contracts

> **RuleSpec** is an open, declarative standard for expressing data validation and governance rules — bridging the gap between static schemas (like JSON Schema or Avro) and executable logic, so that the same rules can run consistently across tools, languages, and platforms.
> This repository contains the official grammar, documentation, examples, and reference tests.

[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![Status](https://img.shields.io/badge/status-draft-orange)]()
[![Made with ❤️ by RuleGenius](https://img.shields.io/badge/made%20by-RuleGenius%20Labs-red)](https://rulegenius.com)
[![Domain](https://img.shields.io/badge/domain-rulespec.org-blue)](https://www.rulespec.org)
[![Type](https://img.shields.io/badge/repo-documentation-blue)]()

It is maintained by [RuleGenius Labs](https://github.com/rulegenius-labs) and powers the commercial [RuleGenius Platform](https://www.rulegenius.com).

---

## Table of Contents
1. [Overview](#overview)
2. [The Problem](#-the-problem)
3. [Why It Matters](#-why-it-matters)
4. [How RuleSpec Solves It](#-how-rulespec-solves-it)
5. [Example RuleSpec Contract](#-example-rulespec-contract)
6. [How It Works Conceptually](#-how-it-works-conceptually)
7. [The Vision](#-the-vision)
8. [For Builders and Businesses](#-for-builders-and-businesses)
9. [Components](#-components)
10. [Comparison with Existing Approaches](#-comparison-with-existing-approaches)
11. [Getting Started](#getting-started)
12. [Contributing](#contributing)
13. [Open Governance Roadmap](#-open-governance-roadmap)
14. [License](#license)
15. [Commercial Implementations](#-commercial-implementations)

---

## Overview

RuleSpec defines a human-readable language (DSL) and open specification for describing how data should behave — not just how it looks.  
It allows teams to express validation and governance rules in a single, portable format that can be executed consistently across tools, pipelines, and organizations.

RuleSpec allows organizations to describe:

- Field-level **validations**
- Cross-field **consistency rules**
- Data **contract metadata** (frequency, retention, fail policy)

All in plain text, with syntax designed for both humans and machines.

---

## 🧩 The Problem

Today’s data systems are **fragmented** when it comes to defining and enforcing **data rules**.  
Every team — and often every pipeline — reinvents the wheel to ensure that incoming data is valid, consistent, and compliant.  

- **Schemas** (like Avro, JSON Schema, or Parquet metadata) only describe the *structure* of data — not its *behavior* or *constraints*.  
- **Code-based validations** (like Python scripts, SQL checks, or Great Expectations suites) are bound to specific frameworks and languages.  
- **Data contracts** are emerging, but lack a common syntax or execution model. Most are just ad hoc YAML conventions or private APIs.  

As a result, organizations face:
- Inconsistent validation logic across tools and teams.  
- Duplicate rule definitions scattered across codebases.  
- Vendor lock-in, as validations can’t move between systems.  
- Weak auditability — it’s unclear *what rules were applied, when, or why*.  

This lack of a shared standard creates a silent cost:  
> “Every company defines its own rules for ‘what good data means’ — but those rules aren’t portable, reusable, or testable outside their home system.”

---

## 🔍 Why It Matters

Data quality is no longer just an engineering concern.  
It’s a **compliance**, **governance**, and **trust** issue.

- In sustainability and ESG reporting, organizations must prove that data was validated under consistent rules.  
- In finance and healthcare, audits demand transparent, version-controlled validation logic.  
- In analytics and machine learning, garbage in still means garbage out — and manual data cleaning doesn’t scale.  

Despite billions spent on “data observability,” there is **no open standard** for declaring validation rules in a consistent, machine-readable, and human-auditable format.  

Just as:
- **SQL** standardized data querying,
- **Avro** standardized data schemas, and
- **Arrow** standardized in-memory data representation,  

the world now needs a **standard for validation and transformation logic**.

---

## ⚙️ How RuleSpec Solves It

**RuleSpec** introduces a **declarative, language-neutral specification** for defining data validation and transformation rules.  

It’s designed to be:
- **Human-readable** → easily reviewed, versioned, and audited.  
- **Machine-executable** → parse once, run anywhere (Python, Java, C++, etc.).  
- **Portable** → independent of any vendor or data platform.  
- **Composable** → multiple rulesets can be chained or merged.  

---

## 📘 Example RuleSpec Contract

```ini
@contract supplier_product_feed_v1
@version 1.0.0
@description "Supplier product data contract"
@format csv delimiter="," encoding="utf-8" max_rows=50000
@on_fail reject

@field product_id type=string required unique
@field price type=number required min=0
@field updated_at type=date required format="YYYY-MM-DD"

validate "product_id" is not_empty
validate "price" is in_range 0..100000
```

Save the example as [`supplier_product_feed_v1.rules`](examples/supplier_product_feed_v1.rules).

This file:
- Defines the data contract (`supplier_product_feed_v1`)
- Declares structure (`@field`) and behavioral rules (`validate`)
- Can be executed by any RuleSpec-compliant engine  
- Produces consistent results — regardless of platform or implementation

---

## 🧠 How It Works Conceptually

RuleSpec provides:
1. **A core language (DSL)** — for expressing validation, transformation, and constraint rules.  
2. **A specification document** — defining the grammar, operators, and data types.  
3. **Reference parsers and APIs** — that translate RuleSpec into executable logic.  
4. **Extensible backends** — enabling integration with Apache Arrow, Spark, Beam, or SQL.  

This decouples *rule definition* from *execution*, enabling:
- Portability across systems.  
- Auditable rule histories (Git + RuleSpec).  
- Shared rule libraries across organizations.  
- Automation in ETL, APIs, or SaaS environments.  

---

## 🌍 The Vision

RuleSpec aims to become the **open standard for portable data contracts** — a foundation layer that any system can build upon.  
It complements existing standards rather than competing with them:

| Layer | Existing Standard | Role |
|-------|--------------------|------|
| **Schema** | Avro / JSON Schema / Parquet | Defines *structure* |
| **Transport** | Arrow / Parquet / CSV | Defines *representation* |
| **Processing** | Beam / Spark / Flink | Defines *execution* |
| **Validation** | **RuleSpec** | Defines *behavior and rules* |

### 🎯 Goals & Non-Goals

**Goals**
- Define a simple, declarative DSL for data validation and governance.
- Enable cross-platform rule portability and interoperability.
- Provide clear, auditable, version-controlled data contracts.
- Maintain human readability and low barrier to adoption.

**Non-Goals**
- Replacing schema formats like Avro or JSON Schema.
- Defining a data storage or serialization layer.
- Building proprietary execution engines within this repository.

---

## 💼 For Builders and Businesses

RuleSpec connects technical and business stakeholders by defining a single source of truth for what constitutes valid data.

- **For developers:** write rules once, run them anywhere.  
- **For data teams:** create version-controlled data contracts that evolve safely.  
- **For auditors:** get human-readable validation evidence, not opaque code.  
- **For vendors:** integrate RuleSpec to ensure interoperability and reduce client lock-in fears.  

By decoupling validation logic from code, **RuleSpec** enables cleaner pipelines, greater transparency, and a shared language for what “good data” means — across systems, organizations and industries.

---

## ⚙️ Components

- **Grammar:** [grammar/rulespec.ebnf](grammar/rulespec.ebnf)  
- **ANTLR Grammar:** [grammar/rulespec.g4](grammar/rulespec.g4)  
- **Docs:** [docs/specification.md](docs/specification.md)  
- **Reference Parser:** [reference/parser_demo.py](reference/parser_demo.py)

---

## 🔬 Comparison with Existing Approaches

| Feature | JSON Schema | Great Expectations | Soda Core | **RuleSpec** |
|----------|--------------|--------------------|------------|---------------|
| Human-readable | ⚙️ Moderate | ⚙️ Complex | ⚙️ Complex | ✅ Simple DSL |
| Portable across systems | ❌ | ❌ | ❌ | ✅ Yes |
| Open standard | ✅ | ❌ | ❌ | ✅ Planned |
| Declarative, vendor-neutral rules | ❌ | ⚙️ | ⚙️ | ✅ |
| Composable pipelines | ❌ | ⚙️ | ⚙️ | ✅ |

---

## Getting Started

RuleSpec source files use the **`.rules`** extension, the shared source filename convention across the RuleGenius project. This avoids confusion with Rust source files and replaces the earlier `.rulespec` convention. The reference CLI is planned; the command below illustrates its intended usage.

```bash
# Validate a CSV file against a rulespec contract
rulespec validate --input products.csv --rules supplier_product_feed_v1.rules
```

Current prototype parsers are being developed in Python and C++, with bindings for Apache Arrow and Pandas.

---

## Contributing

We welcome community input on the RuleSpec syntax, grammar, and use cases.  
To get involved:
- Open a GitHub Discussion or Issue on [rulegenius-labs/rulespec](https://github.com/rulegenius-labs/rulespec)
- Propose new operators, validation patterns, or examples
- Help us test the parser or contribute bindings for new languages

---

## 🧭 Open Governance Roadmap

RuleSpec is currently stewarded by **RuleGenius Labs** under an Apache 2.0 license.  
Our medium-term goal is to establish **neutral governance** under a foundation such as the **Linux Foundation (LF AI & Data)** or the **Apache Software Foundation (ASF)**, ensuring the specification remains open, transparent, and vendor-agnostic.

We welcome feedback from the community on governance, standardization, and interoperability alignment.

---

## 🪶 License

Released under the [Apache 2.0 License](LICENSE).

> “RuleSpec” and “RuleGenius” are trademarks of RuleGenius.  
> Implementations may reference the RuleSpec format but may not use these names for commercial branding without written permission.

---

## 💼 Commercial Implementations

[RuleGenius](https://www.rulegenius.com) provides:

- High-performance validation and data governance engine  
- CLI and API for integrating RuleSpec in production pipelines  
- Managed dashboards and audit logs  

---
**Keywords:** data validation, data contracts, open standard, data quality, RuleGenius, RuleSpec, DSL, Apache Arrow, JSON Schema alternative.
rn more at [rulegenius.com](https://www.rulegenius.com).

