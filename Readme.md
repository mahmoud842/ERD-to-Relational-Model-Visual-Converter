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
