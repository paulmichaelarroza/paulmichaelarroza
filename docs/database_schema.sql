CREATE TABLE roles (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE sites (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE departments (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  site_id INT NOT NULL REFERENCES sites(id),
  UNIQUE(name, site_id)
);

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  full_name VARCHAR(255) NOT NULL,
  hashed_password VARCHAR(255),
  oauth_provider VARCHAR(50),
  oauth_subject VARCHAR(255),
  role_id INT NOT NULL REFERENCES roles(id),
  site_id INT REFERENCES sites(id),
  department_id INT REFERENCES departments(id),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE kras (
  id SERIAL PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  department_id INT NOT NULL REFERENCES departments(id)
);

CREATE TABLE kpis (
  id SERIAL PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  unit_of_measure VARCHAR(50) NOT NULL,
  owner_id INT NOT NULL REFERENCES users(id),
  site_id INT NOT NULL REFERENCES sites(id),
  department_id INT NOT NULL REFERENCES departments(id),
  kra_id INT NOT NULL REFERENCES kras(id)
);

CREATE TABLE kpi_targets (
  id SERIAL PRIMARY KEY,
  kpi_id INT NOT NULL REFERENCES kpis(id),
  period VARCHAR(20) NOT NULL,
  year INT NOT NULL,
  month INT NOT NULL,
  target_value FLOAT NOT NULL,
  UNIQUE(kpi_id, period, year, month)
);

CREATE TABLE kpi_actuals (
  id SERIAL PRIMARY KEY,
  kpi_id INT NOT NULL REFERENCES kpis(id),
  year INT NOT NULL,
  month INT NOT NULL,
  actual_value FLOAT NOT NULL,
  variance FLOAT NOT NULL,
  achievement_percentage FLOAT NOT NULL,
  status VARCHAR(20) NOT NULL,
  created_by INT NOT NULL REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE projects (
  id SERIAL PRIMARY KEY,
  project_name VARCHAR(150) NOT NULL,
  owner_id INT NOT NULL REFERENCES users(id),
  department_id INT NOT NULL REFERENCES departments(id),
  site_id INT NOT NULL REFERENCES sites(id),
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  progress_percentage FLOAT DEFAULT 0,
  status VARCHAR(30) DEFAULT 'Not Started'
);

CREATE TABLE notifications (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id),
  channel VARCHAR(30) NOT NULL,
  message TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE audit_logs (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id),
  action VARCHAR(255) NOT NULL,
  entity VARCHAR(100) NOT NULL,
  entity_id VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
