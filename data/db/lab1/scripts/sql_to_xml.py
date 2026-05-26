
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from xml.dom import minidom

# Rutas de entrada y salida
SQL_FILE = "data/db-sample-schemas-23.3/human_resources/hr_populate.clean.sql"
XML_FILE = "data/xml/hr_populate.xml"

# Columnas de cada tabla en el orden en que aparecen en los VALUES del SQL
TABLE_COLUMNS = {
    "regions":     ["region_id", "region_name"],
    "countries":   ["country_id", "country_name", "region_id"],
    "locations":   ["location_id", "street_address", "postal_code", "city", "state_province", "country_id"],
    "departments": ["department_id", "department_name", "manager_id", "location_id"],
    "jobs":        ["job_id", "job_title", "min_salary", "max_salary"],
    "employees":   ["employee_id", "first_name", "last_name", "email", "phone_number",
                    "hire_date", "job_id", "salary", "commission_pct", "manager_id", "department_id"],
    "job_history": ["employee_id", "start_date", "end_date", "job_id", "department_id"],
}

# Campos que se convierten en atributos XML del elemento fila (se omiten si son NULL)
TABLE_ATTRS = {
    "regions":     ["region_id"],
    "countries":   ["country_id", "region_id"],
    "locations":   ["location_id", "country_id"],
    "departments": ["department_id", "manager_id", "location_id"],
    "jobs":        ["job_id"],
    "employees":   ["employee_id", "job_id", "manager_id", "department_id"],
    "job_history": ["employee_id", "start_date", "end_date", "job_id", "department_id"],
}

# Campos que se convierten en elementos hijo (se omiten si son NULL)
TABLE_CHILDREN = {
    "regions":     ["region_name"],
    "countries":   ["country_name"],
    "locations":   ["street_address", "postal_code", "city", "state_province"],
    "departments": ["department_name"],
    "jobs":        ["job_title", "min_salary", "max_salary"],
    "employees":   ["first_name", "last_name", "email", "phone_number",
                    "hire_date", "salary", "commission_pct"],
    "job_history": [],  # JobHistoryEntry usa solo atributos (elemento auto-cerrado)
}

# Nombre del elemento contenedor de cada tabla en el XML
CONTAINER_TAG = {
    "regions":     "Regions",
    "countries":   "Countries",
    "locations":   "Locations",
    "departments": "Departments",
    "jobs":        "Jobs",
    "employees":   "Employees",
    "job_history": "JobHistory",
}

# Nombre del elemento fila de cada tabla en el XML
ROW_TAG = {
    "regions":     "Region",
    "countries":   "Country",
    "locations":   "Location",
    "departments": "Department",
    "jobs":        "Job",
    "employees":   "Employee",
    "job_history": "JobHistoryEntry",
}

# Captura: INSERT INTO <tabla> VALUES (<valores>);
INSERT_RE = re.compile(
    r"INSERT\s+INTO\s+(\w+)\s+VALUES\s*\((.+?)\)\s*;",
    re.IGNORECASE | re.DOTALL,
)

# Captura la fecha y el formato dentro de TO_DATE('...', '...')
TO_DATE_RE = re.compile(r"TO_DATE\('([^']+)',\s*'([^']+)'\)", re.IGNORECASE)


def tokenize_values(raw: str) -> list[str]:
    """Divide la lista de valores SQL respetando comillas y paréntesis anidados.

    Sin rastrear la profundidad de paréntesis, la coma dentro de
    TO_DATE('fecha', 'formato') se interpretaría como separador de columnas.
    """
    tokens, current, in_quote, depth = [], [], False, 0
    for ch in raw:
        if ch == "'" and not in_quote:
            in_quote = True
            current.append(ch)
        elif ch == "'" and in_quote:
            in_quote = False
            current.append(ch)
        elif not in_quote and ch == "(":
            depth += 1
            current.append(ch)
        elif not in_quote and ch == ")":
            depth -= 1
            current.append(ch)
        elif ch == "," and not in_quote and depth == 0:
            tokens.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        tokens.append("".join(current).strip())
    return tokens


def clean_value(raw: str) -> str | None:
    """Convierte un token SQL a su valor Python equivalente.

    - TO_DATE(...) → cadena ISO 8601 (YYYY-MM-DD)
    - NULL         → None
    - 'texto'      → texto sin comillas
    - número       → cadena tal cual
    """
    raw = raw.strip()
    m = TO_DATE_RE.match(raw)
    if m:
        date_str, fmt = m.group(1), m.group(2)
        py_fmt = fmt.replace("dd", "%d").replace("MM", "%m").replace("yyyy", "%Y")
        return datetime.strptime(date_str, py_fmt).strftime("%Y-%m-%d")
    if raw.upper() == "NULL":
        return None
    if raw.startswith("'") and raw.endswith("'"):
        return raw[1:-1]
    return raw


def format_commission(val: str) -> str:
    # Normaliza a dos decimales: .4 → 0.40
    return f"{float(val):.2f}"


def main():
    with open(SQL_FILE, encoding="utf-8") as f:
        sql = f.read()

    # Diccionario tabla → lista de filas (cada fila es lista de valores limpios)
    tables: dict[str, list[list[str | None]]] = {t: [] for t in TABLE_COLUMNS}

    for m in INSERT_RE.finditer(sql):
        table = m.group(1).lower()
        if table not in tables:
            continue
        values = [clean_value(v) for v in tokenize_values(m.group(2))]
        tables[table].append(values)

    # Elemento raíz con namespace para validación contra el XSD
    root = ET.Element("HumanResources")
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.set("xsi:noNamespaceSchemaLocation", "hr_schema.xsd")

    for table_name, rows in tables.items():
        if not rows:
            continue
        columns    = TABLE_COLUMNS[table_name]
        child_list = TABLE_CHILDREN[table_name]
        container  = ET.SubElement(root, CONTAINER_TAG[table_name])
        row_tag    = ROW_TAG[table_name]

        for row in rows:
            data   = dict(zip(columns, row))
            row_el = ET.SubElement(container, row_tag)

            # IDs y claves foráneas como atributos XML
            for attr in TABLE_ATTRS[table_name]:
                val = data.get(attr)
                if val is not None:
                    row_el.set(attr, val)

            # Datos descriptivos como elementos hijo
            for col in child_list:
                val = data.get(col)
                if val is None:
                    continue
                if col == "commission_pct":
                    val = format_commission(val)
                child = ET.SubElement(row_el, col)
                child.text = val

    # minidom para indentación legible; se corrige la declaración XML
    xml_str = minidom.parseString(ET.tostring(root, encoding="unicode")).toprettyxml(indent="  ")
    lines = xml_str.splitlines()
    if lines[0].startswith("<?xml"):
        lines[0] = '<?xml version="1.0" encoding="UTF-8"?>'
    with open(XML_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    total = sum(len(r) for r in tables.values())
    print(f"Done. {total} rows written to {XML_FILE}")
    for name, rows in tables.items():
        print(f"  {name}: {len(rows)} rows")


if __name__ == "__main__":
    main()
