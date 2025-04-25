DROP TABLE IF EXISTS hired_employees_historical;
DROP TABLE IF EXISTS hired_employees;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS jobs;

CREATE TABLE jobs (
    id INT PRIMARY KEY,
    job VARCHAR(255),
    UNIQUE INDEX idx_jobs_id (id)
);

CREATE TABLE departments (
    id INT PRIMARY KEY,
    department VARCHAR(255),
    UNIQUE INDEX idx_departments_id (id)
);

CREATE TABLE hired_employees (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    datetime VARCHAR(50),
    department_id INT,
    job_id INT,
    load_timestamp TIMESTAMP,
    UNIQUE INDEX idx_hired_employees_id (id)
);

CREATE TABLE hired_employees_historical (
    id INT,
    name VARCHAR(255),
    datetime VARCHAR(50),
    department_id INT,
    job_id INT,
    load_timestamp TIMESTAMP
); 