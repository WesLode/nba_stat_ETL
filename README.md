# nba_stat_ETL

A showcase on ETL process of the NBA data. The dataset include all NBA data from 1983-84 to the current seasons. 

## Getting Started

Install required package
```bash
pip install -r requirements.txt
```

Run Docker for Database

Postgres: 
```bash
# Create a Docker Volume
docker volume create pgdata
```
```bash
# Start the image
docker run --name (image_name) -e POSTGRES_PASSWORD=(your passowrd for postgres) -d postgres -p 5435:5432 -v pgdata:/var/lib/postgresql/data

```

### Export Arguments

