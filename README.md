# weather-monitor
Weather monitor allows users to track weather conditions using weather station(s).

## Tech Stack
### Programming language
Python + Strawberry + FastAPI  
GraphQL - used for all UI integrations -> flexibility in requests  
Rest - for weather station API (probably could be replaced by some kind of queue)  

### DB
The application is trying to monitor weather condition in time > timeseries db. Timescaledb because
it uses standard SQL and can store relation data with time series data as well.

### Caching
N/A; Potentially could be used Redis for basic station data (ie. location)

## APIs
Examples of requests are in /utils folder
### Public API
Allows public access to weather data & station data.

### Weather Station API
Each weather station has API key assigned. This key is used for authentication. This API allows weather stations
store real time weather conditions.

### Administration API
This is used for basic management of weather station - create/update/delete.

User is authenticated via token `{"Authorize": "Bearer <username>"}`.
Users can add/update/delete weather station, limited by 'created by' - user can update/delete only own weather stations.


## Known limitation
1, docker-compose - web service starts before db service is ready (causes fails)  
2, whole authentication is a poor imitation of secure solution (plain text passwords in db, username instead of hashed tokens)  
3, user authentication crashes whole app, works in dev probably only because `--reload` restarts server  
4, mutations could probably be simplified (probably one of two db queries is unnecessary)  
5, some lack of code quality - ie. inconsistency of meteostation vs weather station naming  
6, mypy/flake8 errors  
7, lack of any automated tests  
