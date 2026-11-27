
def validate_file(request_files):
    if 'file' not in request_files:
        return "No se encontró ningún archivo"
    
    file = request_files['file']
    
    if file.filename == '':
        return "No se seleccionó ningún archivo"
    
    if not file.filename.endswith(f'.csv'):
        return "El archivo debe ser un CSV"
   
    return None
    