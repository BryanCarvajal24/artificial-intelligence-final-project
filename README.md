# Qversity Fintech ELT Pipeline

End-to-end ELT pipeline for a fictional LATAM fintech company using Airflow, PostgreSQL, PySpark, dbt, and PowerBI, fully containerized with Docker Compose.

The project ingests raw JSON data from AWS S3, stores it in a Bronze layer, transforms and normalizes it in Silver, and exposes analytics-ready Gold models for business intelligence and dashboards.

---

# Project Information

- Full Name: Bryan Fernando Burbano Carvajal
- Email: bryan.burbano@uao.edu.co
- City: Cali
- Cohort: Qversity Data 2026

---

# Architecture


```text
S3 (fintech_banking_dataset.json)
                │
                ▼
        Apache Airflow (DAG)
                │
                ▼

┌─────────────────────────────────┐
│ BRONZE LAYER                    │
│ PostgreSQL - schema bronze      │
│ Raw JSON stored as jsonb        │
│ + ingestion metadata            │
└─────────────────────────────────┘
                │
                ▼

┌─────────────────────────────────┐
│ PySpark Silver Staging          │
│ - Flatten nested arrays         │
│ - Deduplicate records           │
│ - Create staging tables         │
│ - Write into schema silver      │
└─────────────────────────────────┘
                │
                ▼

┌─────────────────────────────────┐
│ dbt Silver Models               │
│ - Data cleaning                 │
│ - Standardization               │
│ - Normalization                 │
│ - Flatten nested objects        │
│ - Dimensions & facts            │
│ - Data quality tests            │
└─────────────────────────────────┘
                │
                ▼

┌─────────────────────────────────┐
│ GOLD LAYER                      │
│ PostgreSQL - schema gold        │
│ Analytics-ready models          │
│ Business metrics & KPIs         │
└─────────────────────────────────┘
                │
                ▼

          PowerBI Dashboard
```

---

# Bronze Layer

The Bronze layer stores the raw dataset with minimal transformation.

Current implementation:

- Airflow DAG downloads the dataset from AWS S3
- Raw JSON records are stored in PostgreSQL using `jsonb`
- Ingestion metadata is included (`id`, `load_timestamp`)
- Bronze schema and table are automatically created

Main table:

```sql
bronze.raw_fintech_data
```



# Silver Layer

The Silver layer cleans, flattens, normalizes, and structures the Bronze data into relational models.

Current implementation:

- PySpark flattens nested arrays and nested objects
- Deduplication logic is applied
- dbt standardizes and cleans the data
- Fact and dimension tables are created
- Data quality tests are implemented with dbt




# Gold Layer

The Gold layer contains analytics-ready models designed for KPIs, business metrics, and PowerBI dashboards.

Current implementation:

Aggregated business metrics are created
Models are optimized for analytics and reporting
Gold tables support the required business questions
PowerBI connects directly to the gold schema



---

# Start the Project

Start containers:

```bash
docker compose up -d --build
```

Stop containers:

```bash
docker compose down
```

---

# Airflow Access

URL:

```text
http://localhost:8080
```

User:

```text
admin
```

Password:

```text
admin
```

---

# pgAdmin Access

URL:

```text
http://localhost:5050
```

User:

```text
admin@admin.com
```

Password:

```text
admin
```

---

# PostgreSQL/pgAdmin Connection

### **GENERAL**

Name:

```text
ai-project-postgres
```


### **CONNECTION**

Host:

```text
postgres
```

Port:

```text
5432
```

Database:

```text
ai_project
```

User:

```text
ai_admin
```

Password:

```text
ai_admin
```
