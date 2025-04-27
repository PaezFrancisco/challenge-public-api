# Challenge Public API

Esta API permite procesar y analizar datos de empleados, departamentos y trabajos. Está construida con Flask y utiliza Spark para el procesamiento de datos, con MySQL como base de datos.

## Requisitos Previos
- Docker Desktop instalado
- Git instalado
- Mínimo 4GB de RAM disponible
- 2GB de espacio en disco

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/PaezFrancisco/challenge-public-api.git
cd challenge-public-api
```

2. Construir y ejecutar los contenedores:
```bash
docker-compose up --build
```

### Notas específicas por sistema operativo:

#### Windows:
- Asegúrate de que Docker Desktop esté ejecutándose en modo WSL 2
- Si usas PowerShell, ejecuta como administrador
- Puede ser necesario ejecutar:
```powershell
wsl --set-default-version 2
```

#### macOS:
- En Mac con Apple Silicon, asegúrate de que Docker Desktop esté configurado para usar Rosetta 2
- Puede ser necesario aumentar los recursos asignados a Docker Desktop:
  - Abre Docker Desktop
  - Ve a Preferences > Resources
  - Ajusta CPU y memoria según tus necesidades

#### Linux:
- Asegúrate de que tu usuario esté en el grupo docker:
```bash
sudo usermod -aG docker $USER
```
- Reinicia la sesión después de agregar el usuario al grupo

## Uso de la API

Una vez que los contenedores estén en ejecución, la API estará disponible en `http://localhost:8080`

### Endpoints disponibles:

1. **Verificar conexión a base de datos**
   - URL: `http://localhost:8080/db-check`
   - Método: GET
   - Descripción: Verifica la conexión con la base de datos

2. **Cargar datos de jobs o departments**
   - URL: `http://localhost:8080/upload-files-truncate`
   - Método: POST
   - Descripción: Carga y procesa archivos CSV de jobs o departments
   - Asegurate de estar en el mismo directorio donde se encuentrar los archivos: app/files
   - Ejemplo:
   ```bash
   curl -X POST -F "file=@jobs.csv" http://localhost:8080/upload-files-truncate
   ```

3. **Procesar empleados**
   - URL: `http://localhost:8080/process-employees`
   - Método: POST
   - Descripción: Procesa el archivo CSV de empleados
   - Asegurate de estar en el mismo directorio donde se encuentrar los archivos: app/files
   - Ejemplo:
   ```bash
   curl -X POST -F "file=@hired_employees.csv" http://localhost:8080/process-employees
   ```

4. **Query 1: Empleados contratados por trimestre**
   - URL: `http://localhost:8080/query-1`
   - Método: GET
   - Descripción: Muestra el número de empleados contratados por trabajo y departamento en 2021, dividido por trimestre

5. **Query 2: Departamentos con contrataciones superiores al promedio**
   - URL: `http://localhost:8080/query-2`
   - Método: GET
   - Descripción: Lista los departamentos que contrataron más empleados que el promedio en 2021


### Comandos útiles:

```bash
# Ver logs de los contenedores
docker-compose logs -f

# Reiniciar los contenedores
docker-compose restart

# Reconstruir y reiniciar
docker-compose up --build --force-recreate

# Detener y eliminar contenedores
docker-compose down
```

## Estructura del Proyecto

```
challenge-public-api/
├── app/
│   ├── main.py          # Código principal de la API
│   ├── aux.py           # Funciones auxiliares
│   ├── tests.py         # Pruebas unitarias
│   └── files/           # Archivos CSV de datos
│       ├── departments.csv  # Datos de departamentos
│       ├── jobs.csv         # Datos de trabajos
│       └── hired_employees.csv  # Datos de empleados contratados
├── docker-compose.yml   # Configuración de Docker
├── Dockerfile          # Configuración del contenedor de la API
├── requirements.txt    # Dependencias de Python
└── init.sql           # Script de inicialización de la base de datos
```