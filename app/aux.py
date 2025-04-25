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