# Challenge Public API

Esta API permite procesar y analizar datos de empleados, departamentos y trabajos. Está construida con Flask y utiliza Spark para el procesamiento de datos, con MySQL como base de datos.

El enunciado del challenge está en [docs/challenge.pdf](docs/challenge.pdf).

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

Una vez que los contenedores estén en ejecución, la API estará disponible en `http://localhost:8080`.

Los comandos `curl` de abajo se ejecutan desde la raíz del repositorio (los CSV de ejemplo están en `data/`). Se recomienda correrlos en orden.

### Endpoints disponibles:

1. **Verificar conexión a base de datos**
   - URL: `http://localhost:8080/db-check`
   - Método: GET
   - Descripción: Verifica la conexión con la base de datos

2. **Cargar datos de jobs o departments**
   - URL: `http://localhost:8080/upload-files-truncate`
   - Método: POST
   - Descripción: Carga y procesa archivos CSV de jobs o departments (reemplaza el contenido de la tabla)
   - Ejemplo:
   ```bash
   curl -X POST -F "file=@data/jobs.csv" http://localhost:8080/upload-files-truncate
   curl -X POST -F "file=@data/departments.csv" http://localhost:8080/upload-files-truncate
   ```

3. **Procesar empleados**
   - URL: `http://localhost:8080/process-employees`
   - Método: POST
   - Descripción: Guarda el archivo completo en `hired_employees_historical` y hace un upsert de los registros válidos en `hired_employees`
   - Ejemplo:
   ```bash
   curl -X POST -F "file=@data/hired_employees.csv" http://localhost:8080/process-employees
   ```

4. **Query 1: Empleados contratados por trimestre**
   - URL: `http://localhost:8080/query-1`
   - Método: GET
   - Descripción: Muestra el número de empleados contratados por trabajo y departamento en 2021, dividido por trimestre

5. **Query 2: Departamentos con contrataciones superiores al promedio**
   - URL: `http://localhost:8080/query-2`
   - Método: GET
   - Descripción: Lista los departamentos que contrataron más empleados que el promedio en 2021

Las queries se ven como tabla HTML desde el navegador y como tabla de texto desde la terminal:
```bash
curl http://localhost:8080/query-1
```

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
│   ├── main.py          # API Flask: endpoints, schemas y procesamiento con Spark
│   ├── render.py        # Renderizado de resultados (tabla HTML o texto plano)
│   └── validators.py    # Validación de los archivos recibidos
├── data/                # CSV de ejemplo para cargar en la API
│   ├── departments.csv
│   ├── hired_employees.csv
│   └── jobs.csv
├── db/
│   └── init.sql         # Creación de tablas al iniciar MySQL
├── docs/
│   └── challenge.pdf    # Enunciado del challenge
├── docker-compose.yml   # Servicios de MySQL y la API
├── Dockerfile           # Imagen de la API (Python + Java para Spark)
└── requirements.txt     # Dependencias de Python
```

## Próximas mejoras

- Separar `main.py` en módulos: configuración, schemas de Spark, acceso a datos y rutas (Flask Blueprints).
- Agregar tests automatizados con `pytest` para validaciones, renderizado y endpoints.
- Servir la API con un servidor WSGI (por ejemplo `gunicorn`) en lugar de `flask run`.
