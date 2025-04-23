
def validate_file(request_files, name):
    if 'file' not in request_files:
        return "No se encontró ningún archivo"
    
    file = request_files['file']
    
    if file.filename == '':
        return "No se seleccionó ningún archivo"
    
    if not file.filename.endswith(f'{name}.csv'):
        return "El archivo debe ser un CSV"
   
    return None
    