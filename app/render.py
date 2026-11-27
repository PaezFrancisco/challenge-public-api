from decimal import Decimal

from flask import Response, request


def render_table(header, columns, rows):
    # El navegador manda "text/html" en el header Accept; curl manda "*/*".
    # Asi el mismo endpoint se ve como tabla HTML en el navegador y como texto en la terminal.
    if "text/html" in request.headers.get("Accept", ""):
        return create_table(header, columns, rows)
    return Response(create_text_table(header, columns, rows), mimetype="text/plain")


def create_text_table(header, columns, rows):
    # Crear tabla en texto plano (estilo cliente de MySQL) para verla en la terminal
    widths = [max([len(column)] + [len(str(row[column])) for row in rows]) for column in columns]
    separator = "+" + "+".join("-" * (width + 2) for width in widths) + "+"

    lines = [header, separator]
    lines.append("| " + " | ".join(column.ljust(width) for column, width in zip(columns, widths)) + " |")
    lines.append(separator)
    for row in rows:
        cells = []
        for column, width in zip(columns, widths):
            value = row[column]
            # Numeros alineados a la derecha, texto a la izquierda
            if isinstance(value, (int, float, Decimal)):
                cells.append(str(value).rjust(width))
            else:
                cells.append(str(value).ljust(width))
        lines.append("| " + " | ".join(cells) + " |")
    lines.append(separator)
    lines.append(f"{len(rows)} filas")

    return "\n".join(lines) + "\n"


def create_table(header, columns, rows):
     # Crear tabla HTML
        html_table = f"""
        <style>
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                font-family: Arial, sans-serif;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            h2 {{
                color: #333;
                font-family: Arial, sans-serif;
                margin-bottom: 20px;
            }}
        </style>
        <h2>{header}</h2>
        <table>
            <tr> """
        for column in columns:
            html_table += f""" <th>{column}</th>"""
        html_table += """</tr>"""       

        for row in rows:
            html_table += "<tr>"
            for column in columns:
                html_table += f"<td>{row[column]}</td>"
            html_table += "</tr>"
        html_table += """
            </table>
        """
        
        return html_table