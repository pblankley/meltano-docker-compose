## Meltano with `docker-compose`

## Get started 

Run this in the root directory to bring all containers up running in the background
```
docker-compose up --build -d 
```

To check the logs you can run `docker-compose logs`


This is a simple example of meltano with `docker-compose` and postgres.  This system runs a postgres instance with separate databases to hold the metadata of both meltano and airflow (which is what you'll want to do in production). It also runs a container with the meltano ui, the airflow webserver, and the airflow scheduler that is running LocalExecutor.


### Containers

1. postgres
2. meltano ui
3. airflow webserver
4. airflow scheduler

