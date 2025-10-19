from typing import Dict, List, Any, Optional
from graphviz import Digraph

def add_column(
    tables,
    table_name,
    col_name,
    primary = False,
    foreign = False,
    references = None,
):
    tables[table_name].append(
        {"name": col_name, "primary": primary, "foreign": foreign, "references": references}
    )

def add_fks(
    tables,
    entity_pk_components,
    target_table,
    ref_table,
):
    ref_pks = entity_pk_components.get(ref_table, [])
    for pk in ref_pks:
        add_column(
            tables,
            target_table,
            pk,
            foreign=True,
            references={"table": ref_table, "attribute": pk},
        )

def generate_tables(data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    tables: Dict[str, List[Dict[str, Any]]] = {}
    entity_pk_components: Dict[str, List[str]] = {}
    multivalued = []
    weak_entities = set()

    # entities
    for entity in data["entities"]:
        ent_name = entity["name"]
        tables[ent_name] = []
        entity_pk_components[ent_name] = []

        if entity.get("isWeak", False):
            weak_entities.add(ent_name)

        for attribute in entity["attributes"]:
            att_name = attribute["name"]
            is_primary = attribute.get("isPrimaryKey", False) or attribute.get("isPartialKey", False)
            is_multi = attribute.get("isMultiValued", False)
            comp = attribute.get("composite")

            if is_multi:
                multivalued.append((ent_name, attribute))
                continue

            if comp:
                for part in comp:
                    col_name = f"{att_name}_{part}"
                    add_column(tables, ent_name, col_name, primary=is_primary)
                    if is_primary:
                        entity_pk_components[ent_name].append(col_name)
            else:
                add_column(tables, ent_name, att_name, primary=is_primary)
                if is_primary:
                    entity_pk_components[ent_name].append(att_name)

    # relationships
    for relation in data.get("relationships", []):
        rel_name = relation.get("name")
        ents = relation.get("entities", [])
        rel_attrs = relation.get("attributes", [])
        is_ident = relation.get("isIdentifying", False)

        # n-ary relation → its own table
        if len(ents) != 2:
            rt = rel_name
            tables[rt] = []
            for p in ents:
                p_name = p["name"]
                for pk in entity_pk_components.get(p_name, []):
                    add_column(
                        tables,
                        rt,
                        f"{p_name}_{pk}",
                        primary=True,
                        foreign=True,
                        references={"table": p_name, "attribute": pk},
                    )
            for a in rel_attrs:
                add_column(tables, rt, a["name"])
            continue

        left, right = ents
        left_name, right_name = left["name"], right["name"]
        left_card, right_card = left.get("cardinality", "1"), right.get("cardinality", "1")

        # identifying (weak) relationship
        if is_ident:
            weak_ent = owner_ent = None
            if left_name in weak_entities:
                weak_ent, owner_ent = left_name, right_name
            elif right_name in weak_entities:
                weak_ent, owner_ent = right_name, left_name
            if weak_ent and owner_ent:
                for pk in entity_pk_components.get(owner_ent, []):
                    add_column(
                        tables,
                        weak_ent,
                        f"{owner_ent}_{pk}",
                        primary=True,
                        foreign=True,
                        references={"table": owner_ent, "attribute": pk},
                    )
                for a in rel_attrs:
                    add_column(tables, weak_ent, a["name"])
                continue

        # cardinalities
        if (left_card == "1") and (right_card == "1"):
            add_fks(tables, entity_pk_components, left_name, right_name)
        elif (left_card == "1") and (right_card.upper() == "N"):
            add_fks(tables, entity_pk_components, right_name, left_name)
        elif (right_card == "1") and (left_card.upper() == "N"):
            add_fks(tables, entity_pk_components, left_name, right_name)
        else:
            joint_name = rel_name
            tables[joint_name] = []

            for pk in entity_pk_components.get(left_name, []):
                add_column(
                    tables,
                    joint_name,
                    f"{left_name}_{pk}",
                    primary=True,
                    foreign=True,
                    references={"table": left_name, "attribute": pk},
                )

            for pk in entity_pk_components.get(right_name, []) :
                add_column(
                    tables,
                    joint_name,
                    f"{right_name}_{pk}",
                    primary=True,
                    foreign=True,
                    references={"table": right_name, "attribute": pk},
                )
                
            for a in rel_attrs:
                add_column(tables, joint_name, a["name"])

    # multivalued attributes
    for ent_name, attr in multivalued:
        att_name = attr["name"]
        comp = attr.get("composite")

        mv_table = f"{ent_name}_{att_name}"
        tables[mv_table] = []

        for pk in entity_pk_components.get(ent_name, []):
            add_column(
                tables,
                mv_table,
                f"{ent_name}_{pk}",
                primary=True,
                foreign=True,
                references={"table": ent_name, "attribute": pk},
            )

        if comp:
            for part in comp:
                add_column(tables, mv_table, f"{att_name}_{part}", primary=True)
        else:
            add_column(tables, mv_table, att_name, primary=True)

    # order columns (PKs first)
    for _, cols in tables.items():
        cols.sort(key=lambda c: (not c["primary"], c["name"]))

    return tables
