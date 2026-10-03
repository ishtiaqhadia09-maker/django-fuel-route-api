# Django Fuel Route API

A Django REST API that calculates a driving route between two US locations and identifies cost-effective fuel stops along the route using the provided fuel-price dataset.

## Overview

The API accepts a starting location and a destination within the United States.

It:

1. Geocodes the start and finish locations.
2. Calculates the driving route.
3. Finds fuel stations along the route.
4. Matches those stations with the provided fuel-price dataset.
5. Selects fuel stops while respecting the vehicle's maximum range.
6. Calculates the estimated fuel cost using 10 MPG.
7. Returns the route geometry so a client can render the route on a map.

## Requirements

* Python 3.10+
* Django
* Django REST Framework
* PostgreSQL
* Geoapify API key

## Tech Stack

* Python
* Django
* Django REST Framework
* PostgreSQL
* Geoapify Geocoding API
* Geoapify Routing API
* Geoapify Places API
* Requests

## Project Structure

```text
django-fuel-route-api/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── routes/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   │
│   ├── services/
│   │   ├── routing.py
│   │   ├── fuel.py
│   │   ├── matching.py
│   │   └── optimizer.py
│   │
│   └── management/
│       └── commands/
│           └── import_fuel_prices.py
│
├── data/
│   └── fuel-prices-for-be-assessment.csv
│
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
└── README.md
```

## Architecture

The application uses a simple service-layer architecture.

### RoutingService

Responsible for:

* Geocoding start and finish locations.
* Calling the Geoapify routing API.
* Returning route distance, duration and geometry.

### FuelStationService

Responsible for:

* Finding fuel stations along the calculated route using Geoapify Places.

### FuelStationMatcher

Responsible for:

* Matching Geoapify fuel stations against the stations in the provided dataset.
* Restricting matched stations to US states.
* Using station name, city and address similarity.

### FuelOptimizer

Responsible for:

* Positioning fuel stations along the route.
* Respecting the vehicle's 500-mile maximum range.
* Selecting cost-effective fuel stops.
* Calculating fuel consumption and cost.

This separation keeps the API view focused on orchestration while the individual services handle specific responsibilities.

## Fuel Assumptions

The assignment specifies:

* Maximum vehicle range: **500 miles**
* Fuel economy: **10 miles per gallon**

The optimizer uses these values when determining feasible fuel stops and calculating fuel costs.

## Fuel Price Dataset

The supplied CSV dataset is imported into PostgreSQL using a Django management command.

Run:

```bash
python manage.py import_fuel_prices
```

The dataset contains station information including:

* Station ID
* Station name
* Address
* City
* State
* Rack ID
* Retail price

## Environment Variables

Create a `.env` file in the project root:

```env
GEOAPIFY_API_KEY=your_api_key_here
```

Database credentials should also be configured through environment variables when running the application outside the local development environment.

Do not commit `.env` or API keys to GitHub.

## Running the Project

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd django-fuel-route-api
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL database and configure the database settings in Django.

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Import fuel prices

```bash
python manage.py import_fuel_prices
```

### 7. Start the development server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

## API Endpoint

### Calculate Route

```http
POST /api/route/
```

### Request

```json
{
    "start": "New York, NY",
    "finish": "Chicago, IL"
}
```

### Response

```json
{
    "route": {
        "start": "New York, NY",
        "finish": "Chicago, IL",
        "distance_miles": 791.79,
        "duration_minutes": 735.5
    },
    "fuel": {
        "mpg": 10,
        "max_range_miles": 500,
        "gallons_purchased": 29.18,
        "total_cost": 105.42
    },
    "fuel_stops": [
        {
            "station": "EXAMPLE STATION",
            "city": "Example City",
            "state": "PA",
            "price_per_gallon": 3.079,
            "distance_from_start_miles": 184.25
        }
    ],
    "map": {
        "geometry": [
            {
                "lat": 40.7128,
                "lon": -74.006
            }
        ]
    }
}
```

The exact fuel stops, gallons and cost depend on the requested route and the supplied fuel-price dataset.

## API Validation

The API validates the required request fields.

For example, a request without a destination:

```json
{
    "start": "New York, NY"
}
```

returns HTTP `400 Bad Request`.

## External API Usage

Geoapify is used for:

* Geocoding
* Route calculation
* Finding fuel stations along the route

The route geometry is reused when finding fuel stations so the application does not repeatedly calculate the same route.

Fuel stations are discovered along sections of the existing route, allowing the application to keep external API usage limited.

## Performance

The application is designed to avoid unnecessary routing API calls.

The route is calculated once and the resulting geometry is reused for fuel-station discovery.

The API also simplifies the returned route geometry before sending it to the client, reducing the response size while retaining enough information to render the route.

## Design Decisions

### PostgreSQL

PostgreSQL is used as the database because the application works with structured fuel-station data and benefits from database-level filtering.

### Service Layer

External API calls, station matching and fuel optimization are separated into services instead of placing all logic inside the Django view.

This makes the code easier to understand, test and maintain.

### Dataset Matching

The provided fuel-price dataset does not contain latitude and longitude for every station. Therefore, external fuel-station results are matched against the supplied dataset using station information such as name, city, state and address.

## License

This project was created as part of a Backend Django Engineer technical assessment.
