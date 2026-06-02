# Application of Artificial Intelligence Algorithms for PM2.5 Prediction in Eastern Santiago de Cali

End-to-end Data Engineering and Artificial Intelligence pipeline for PM2.5 prediction in the eastern area of Santiago de Cali, Colombia, using Apache Airflow, PostgreSQL, Docker, XGBoost, and Power BI, fully containerized with Docker Compose.

The project combines historical air quality records collected between 2014 and 2019 from the Compartir Air Quality Monitoring Station, located in eastern Santiago de Cali, with real-time environmental data acquired from two monitoring systems installed at Fundautónoma: a PurpleAir sensor for PM10 measurements and an Ambient Weather station for meteorological observations.

The pipeline ingests raw environmental and air quality data into a Bronze layer, performs cleaning, transformation, feature engineering, and PM10 integration in a Silver layer, and exposes PM2.5 predictions through analytics-ready Gold models for monitoring, reporting, and visualization.

An XGBoost regression model is trained using historical observations from the Compartir monitoring station and subsequently used to estimate PM2.5 concentrations from current meteorological conditions and PM10 measurements collected in eastern Santiago de Cali.

---

# Project Information

- Full Name: Bryan Fernando Burbano Carvajal
- Email: bryanburbanocarvajal24@gmail.com
- City: Cali
- Role: Data Engineer and Artificial Intelligence Engineer

---

Teammates:

- Samuel Uribe
- Emilio Marquez
- Juan Pablo Lopez

---




# Architecture


```text


                 Apache Airflow DAG
                            │
                            ▼

Ambient Weather API                 PurpleAir API
         │                                 │
         ▼                                 ▼

┌─────────────────────────────────────────────────────┐
│ BRONZE LAYER                                        │
│ PostgreSQL - Schema: bronze                         │
│                                                     │
│ bronze.ambient_weather_api_data                     │
│ bronze.PM10_station_api_data                        │
│                                                     │
│ • Raw meteorological data                           │
│ • Raw PM10 measurements                             │
│ • API ingestion layer                               │
└─────────────────────────────────────────────────────┘
                             │
                             ▼

┌─────────────────────────────────────────┐
│ SILVER LAYER                            │
│ silver.stg_environmental_api_data       │
│                                         │
│ - Data cleaning                         │
│ - Datetime processing                   │
│ - Feature engineering                   │
│ - Cyclical variables                    │
│ - PM10 merge                            │
└─────────────────────────────────────────┘
                             │
                             ▼

┌─────────────────────────────────────────┐
│ HISTORICAL DATASET                      │
│ silver.stg_historical_compartir_station │
│                                         │
│ - Air pollutant variables               │
│ - Meteorological variables              │
│ - Training features                     │
└─────────────────────────────────────────┘
                             │
                             ▼

┌─────────────────────────────────────────┐
│ MACHINE LEARNING                        │
│ XGBoost Regressor                       │
│                                         │
│ - Model training                        │
│ - Feature persistence                   │
│ - Model persistence (.pkl)              │
└─────────────────────────────────────────┘
                             │
                             ▼

┌─────────────────────────────────────────┐
│ GOLD LAYER                              │
│ gold.pm25_predictions                   │
│                                         │
│ - Environmental variables               │
│ - Predicted PM2.5 values                │
│ - Analytics-ready dataset               │
└─────────────────────────────────────────┘
                             │
                             ▼

                     Power BI Dashboard


```




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



# Power BI Connection

## GET DATA

Select:

```text
PostgreSQL Database
```

---

## DATABASE

### Server

```text
localhost:5432
```

### Database

```text
ai_project
```

### Data Connectivity Mode

```text
Import
```

Click **OK**.

---

## AUTHENTICATION

### Username

```text
ai_admin
```

### Password

```text
ai_admin
```

### Apply Settings To

```text
localhost:5432
```

Click **Connect**.

---

## ENCRYPTION COMPATIBILITY

When connecting, Power BI may display the following message:

```text
Compatibility with encryption
```

Message:

```text
Unable to connect to the data source through an encrypted connection.
To access this data source using an unencrypted connection, click Accept.
```

Action:

```text
Click Accept
```

Power BI will then establish the connection successfully.


```text
Transform Data
```

