# ERD-to-Relational Model Visual Converter

## 📘 Objective
This project automatically converts an **Entity–Relationship Diagram (ERD)**, provided in **JSON format**, into a **visual Relational Model diagram**.

The output diagram shows:
- Each entity as a table with its attributes
- **Primary keys** underlined and bold
- **Foreign keys** italicized
- **Arrows** indicating relationships between tables

---

## 🧩 Description
The program reads a structured JSON file describing entities and relationships, applies **ER-to-Relational transformation rules**, and generates a **relational schema diagram** using Graphviz.

Main features:
- Converts entities and relationships to relational tables
- Handles **composite**, **multivalued**, **primary**, **partial**, and **weak** attributes
- Supports identifying and non-identifying relationships
- Produces a **.png diagram** showing all tables and foreign key links

---

## ⚙️ How the Code Works

| Stage | Module / Function | Description |
|--------|-------------------|--------------|
| **1. JSON Loading** | `load_json()` in `script.py` | Reads and parses the ERD JSON file, handling errors like missing or invalid files. |
| **2. Table Generation** | `generate_tables()` in `build_table.py` | Transforms entities and relationships into relational tables according to ER mapping rules. |
| **3. Column Management** | `add_column()`, `add_fks()` | Adds attributes to tables, labeling primary and foreign keys and their references. |
| **4. Visualization** | `tables_to_graph()` in `render.py` | Builds and renders the final relational schema diagram using Graphviz table nodes and arrows. |
| **5. Execution Flow** | Main block (`if __name__ == "__main__":`) | Orchestrates the workflow: load → transform → render. |

### Example Command:
```bash
python script.py input.json
```

---

## 🧠 Main Libraries Used

| Library | Purpose |
|----------|----------|
| `json` | Parses the ERD description from a JSON file. |
| `os`, `sys` | Handles command-line arguments and file paths. |
| `typing` | Adds type hints for cleaner, safer code. |
| `graphviz` | Generates and renders the relational schema diagram as a PNG image. |

---

## 📋 Assumptions
1. Input JSON strictly follows the lab specification (must include `entities` and `relationships`).
2. Each entity has a unique name.
3. Attributes may be **simple**, **composite**, **multivalued**, or **key** (primary/partial).
4. Relationships specify participating entities and cardinalities (`1`, `N`, etc.).
5. Weak entities are marked with `"isWeak": true`, and identifying relationships use `"isIdentifying": true`.
6. The system has **Graphviz** installed and available in the PATH.

---

## 🧾 Conclusion
This tool automates the ER-to-Relational mapping process, ensuring consistency and accuracy.  
It produces clear, visual representations of relational schemas and demonstrates strong understanding of database modeling concepts combined with practical Python implementation.

---

# Linear Algebra–Style Relational Query Executor

## 📘 Objective
This part of the lab implements a **Linear Algebra–style Query Executor** that performs **relational algebra operations** on datasets represented as JSON tables.  
It supports executing formulas like `SELECT`, `PROJECT`, `JOIN`, `UNION`, `INTERSECT`, `DIFFERENCE`, and `AGGREGATE` on tabular data without using external libraries such as pandas.

---

## 🧩 Description
The program reads one or more datasets from a **JSON file**, parses a **formula string** representing a relational query, and executes it step by step.

It supports:
- Loading multiple tables from a JSON input.
- Parsing nested relational expressions.
- Evaluating expressions recursively using relational operations.
- Writing results to `output.csv` and printing them in tabular form.

---

## ⚙️ How the Code Works

| Stage | Module / Function | Description |
|--------|-------------------|--------------|
| **1. Parsing** | `split_top_level_commas()` and `parse_formula()` | Parse the relational expression into operation and arguments while handling nested parentheses and string literals. |
| **2. Formula Evaluation** | `eval_formula()` | Recursively evaluates relational expressions (SELECT, PROJECT, JOIN, UNION, INTERSECT, DIFFERENCE, AGGREGATE). |
| **3. Relational Operations** | Defined in `operations.py` | Each relational operation (select, project, join, etc.) is implemented manually using Python loops and conditions. |
| **4. Expression Evaluation** | `make_eval_func()` | Safely compiles and evaluates condition expressions for SELECT and JOIN using Python's eval in a controlled environment. |
| **5. Output** | `print_table()` and `write_csv()` | Displays the final result as a formatted table and saves it to a CSV file. |

### Example Command:
```bash
python main.py data.json "SELECT(Employee, Salary > 5000)"
```

---

## 🧠 Main Libraries Used

| Library | Purpose |
|----------|----------|
| `json` | Reads and parses JSON input files. |
| `csv` | Exports results to a CSV file. |
| `sys` | Reads command-line arguments. |
| `typing` | Adds static type hints for code clarity. |

---

## 📋 Supported Operations

| Operation | Description |
|------------|--------------|
| `SELECT(table, condition)` | Filters rows based on a boolean condition. |
| `PROJECT(table, [fields])` | Selects specific attributes (columns). |
| `JOIN(A, B, condition)` | Combines tuples from two tables where a condition is true. |
| `UNION(A, B)` | Returns all tuples present in A or B (duplicates removed). |
| `INTERSECT(A, B)` | Returns only tuples common to both A and B. |
| `DIFFERENCE(A, B)` | Returns tuples in A that are not in B. |
| `AGGREGATE(table, [group_by], FUNC(field))` | Computes aggregate functions (SUM, AVG, MIN, MAX, COUNT). |

---

## 📋 Assumptions
1. Input JSON must follow a dictionary format where each key is a table name and each value is a list of row dictionaries.  
2. Formulas follow the format `OPERATION(arg1, arg2, ...)` and can be nested.  
3. Arithmetic and comparison operators in conditions follow standard Python syntax.  
4. Aggregate functions only support numeric fields (except COUNT).  
5. Output CSV is written to the current working directory as `output.csv`.

---

## 🧾 Conclusion
This implementation provides a **lightweight in-memory relational algebra engine**.  
It mimics linear algebra–style query execution by combining recursive parsing and Python evaluation.  
The system demonstrates understanding of **relational algebra**, **query processing**, and **data manipulation** using core Python features without relying on external frameworks.

---
