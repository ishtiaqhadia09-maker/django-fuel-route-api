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
git clone https://github.com/ishtiaqhadia09-maker/django-fuel-route-api.git
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
        "duration_minutes": 721.53
    },
    "fuel": {
        "mpg": 10,
        "gallons_purchased": 30.69,
        "total_cost": 109.49
    },
    "fuel_stops": [
        {
            "station": "VALERO",
            "city": "Clinton",
            "state": "NJ",
            "price_per_gallon": 3.359,
            "distance_from_start_miles": 2.58
        },
        {
            "station": "MOBIL",
            "city": "Columbia",
            "state": "NJ",
            "price_per_gallon": 3.079,
            "distance_from_start_miles": 43.43
        },
        {
            "station": "SUNOCO",
            "city": "Lock Haven",
            "state": "PA",
            "price_per_gallon": 3.599,
            "distance_from_start_miles": 184.25
        },
        {
            "station": "EXXON",
            "city": "Lawrenceville",
            "state": "PA",
            "price_per_gallon": 3.699,
            "distance_from_start_miles": 306.9
        }
    ],
    "map": {
        "geometry": [
            {
                "lon": -74.006225,
                "lat": 40.712491
            },
            {
                "lon": -74.008686,
                "lat": 40.719371
            },
            {
                "lon": -74.007598,
                "lat": 40.725773
            },
            {
                "lon": -74.038057,
                "lat": 40.731411
            },
            {
                "lon": -74.050798,
                "lat": 40.731173
            },
            {
                "lon": -74.062046,
                "lat": 40.739035
            },
            {
                "lon": -74.067732,
                "lat": 40.739485
            },
            {
                "lon": -74.066421,
                "lat": 40.740501
            },
            {
                "lon": -74.078637,
                "lat": 40.739698
            },
            {
                "lon": -74.091207,
                "lat": 40.744554
            },
            {
                "lon": -74.102865,
                "lat": 40.746329
            },
            {
                "lon": -74.123346,
                "lat": 40.75047
            },
            {
                "lon": -74.13266,
                "lat": 40.746274
            },
            {
                "lon": -74.152259,
                "lat": 40.742372
            },
            {
                "lon": -74.161513,
                "lat": 40.746786
            },
            {
                "lon": -74.170351,
                "lat": 40.747731
            },
            {
                "lon": -74.18395,
                "lat": 40.751024
            },
            {
                "lon": -74.193268,
                "lat": 40.752929
            },
            {
                "lon": -74.206737,
                "lat": 40.758659
            },
            {
                "lon": -74.240167,
                "lat": 40.77285
            },
            {
                "lon": -74.250552,
                "lat": 40.80091
            },
            {
                "lon": -74.254518,
                "lat": 40.809041
            },
            {
                "lon": -74.268797,
                "lat": 40.81265
            },
            {
                "lon": -74.28498,
                "lat": 40.817856
            },
            {
                "lon": -74.294529,
                "lat": 40.820783
            },
            {
                "lon": -74.308401,
                "lat": 40.81436
            },
            {
                "lon": -74.334535,
                "lat": 40.834441
            },
            {
                "lon": -74.3534,
                "lat": 40.849311
            },
            {
                "lon": -74.37374,
                "lat": 40.859113
            },
            {
                "lon": -74.413362,
                "lat": 40.863728
            },
            {
                "lon": -74.457966,
                "lat": 40.86891
            },
            {
                "lon": -74.472072,
                "lat": 40.887107
            },
            {
                "lon": -74.488811,
                "lat": 40.898743
            },
            {
                "lon": -74.512618,
                "lat": 40.911365
            },
            {
                "lon": -74.581055,
                "lat": 40.907969
            },
            {
                "lon": -74.610027,
                "lat": 40.904942
            },
            {
                "lon": -74.666067,
                "lat": 40.892849
            },
            {
                "lon": -74.70489,
                "lat": 40.890905
            },
            {
                "lon": -74.720601,
                "lat": 40.901888
            },
            {
                "lon": -74.743711,
                "lat": 40.912596
            },
            {
                "lon": -74.766206,
                "lat": 40.916073
            },
            {
                "lon": -74.783073,
                "lat": 40.924189
            },
            {
                "lon": -74.802942,
                "lat": 40.921503
            },
            {
                "lon": -74.823831,
                "lat": 40.91797
            },
            {
                "lon": -74.845065,
                "lat": 40.919787
            },
            {
                "lon": -74.888496,
                "lat": 40.929131
            },
            {
                "lon": -74.947154,
                "lat": 40.925076
            },
            {
                "lon": -74.971561,
                "lat": 40.929191
            },
            {
                "lon": -75.022794,
                "lat": 40.93405
            },
            {
                "lon": -75.06919,
                "lat": 40.927601
            },
            {
                "lon": -75.097113,
                "lat": 40.930352
            },
            {
                "lon": -75.113998,
                "lat": 40.952041
            },
            {
                "lon": -75.120328,
                "lat": 40.970676
            },
            {
                "lon": -75.135704,
                "lat": 40.977678
            },
            {
                "lon": -75.154094,
                "lat": 40.998457
            },
            {
                "lon": -75.196682,
                "lat": 40.979017
            },
            {
                "lon": -75.230721,
                "lat": 40.98594
            },
            {
                "lon": -75.300675,
                "lat": 41.015491
            },
            {
                "lon": -75.348622,
                "lat": 41.064605
            },
            {
                "lon": -75.397044,
                "lat": 41.074382
            },
            {
                "lon": -75.449695,
                "lat": 41.071997
            },
            {
                "lon": -75.579905,
                "lat": 41.076855
            },
            {
                "lon": -75.612271,
                "lat": 41.079438
            },
            {
                "lon": -75.678737,
                "lat": 41.074657
            },
            {
                "lon": -75.725917,
                "lat": 41.056257
            },
            {
                "lon": -75.798753,
                "lat": 41.056355
            },
            {
                "lon": -75.924426,
                "lat": 41.059659
            },
            {
                "lon": -76.043866,
                "lat": 41.03906
            },
            {
                "lon": -76.118063,
                "lat": 41.016954
            },
            {
                "lon": -76.15051,
                "lat": 41.004531
            },
            {
                "lon": -76.168845,
                "lat": 41.016395
            },
            {
                "lon": -76.197125,
                "lat": 41.017147
            },
            {
                "lon": -76.238083,
                "lat": 41.009599
            },
            {
                "lon": -76.277481,
                "lat": 41.013199
            },
            {
                "lon": -76.300451,
                "lat": 41.013462
            },
            {
                "lon": -76.357975,
                "lat": 41.03922
            },
            {
                "lon": -76.44303,
                "lat": 41.026639
            },
            {
                "lon": -76.503224,
                "lat": 41.009283
            },
            {
                "lon": -76.552074,
                "lat": 41.007336
            },
            {
                "lon": -76.600007,
                "lat": 41.001655
            },
            {
                "lon": -76.682895,
                "lat": 40.989586
            },
            {
                "lon": -76.74424,
                "lat": 40.996181
            },
            {
                "lon": -76.800026,
                "lat": 41.024705
            },
            {
                "lon": -76.85383,
                "lat": 41.051843
            },
            {
                "lon": -76.925367,
                "lat": 41.076036
            },
            {
                "lon": -77.0749,
                "lat": 41.064399
            },
            {
                "lon": -77.14709,
                "lat": 41.049863
            },
            {
                "lon": -77.204048,
                "lat": 41.053661
            },
            {
                "lon": -77.218363,
                "lat": 41.065315
            },
            {
                "lon": -77.321651,
                "lat": 41.048322
            },
            {
                "lon": -77.392109,
                "lat": 41.060847
            },
            {
                "lon": -77.424752,
                "lat": 41.064679
            },
            {
                "lon": -77.480308,
                "lat": 41.038219
            },
            {
                "lon": -77.581584,
                "lat": 41.01779
            },
            {
                "lon": -77.621643,
                "lat": 40.983794
            },
            {
                "lon": -77.703159,
                "lat": 40.948036
            },
            {
                "lon": -77.755875,
                "lat": 40.95541
            },
            {
                "lon": -77.817889,
                "lat": 40.989064
            },
            {
                "lon": -77.9123,
                "lat": 41.025061
            },
            {
                "lon": -77.966861,
                "lat": 41.008406
            },
            {
                "lon": -78.046797,
                "lat": 40.975855
            },
            {
                "lon": -78.102379,
                "lat": 40.962578
            },
            {
                "lon": -78.132698,
                "lat": 40.980579
            },
            {
                "lon": -78.185905,
                "lat": 40.985992
            },
            {
                "lon": -78.263245,
                "lat": 40.994823
            },
            {
                "lon": -78.328346,
                "lat": 41.015007
            },
            {
                "lon": -78.375824,
                "lat": 41.030895
            },
            {
                "lon": -78.412956,
                "lat": 41.04166
            },
            {
                "lon": -78.467239,
                "lat": 41.067177
            },
            {
                "lon": -78.507294,
                "lat": 41.084209
            },
            {
                "lon": -78.595802,
                "lat": 41.125549
            },
            {
                "lon": -78.729721,
                "lat": 41.136429
            },
            {
                "lon": -78.805542,
                "lat": 41.152684
            },
            {
                "lon": -78.864086,
                "lat": 41.150568
            },
            {
                "lon": -78.968961,
                "lat": 41.138095
            },
            {
                "lon": -79.002124,
                "lat": 41.160749
            },
            {
                "lon": -79.040922,
                "lat": 41.167955
            },
            {
                "lon": -79.085283,
                "lat": 41.170574
            },
            {
                "lon": -79.136564,
                "lat": 41.18047
            },
            {
                "lon": -79.194436,
                "lat": 41.185766
            },
            {
                "lon": -79.242154,
                "lat": 41.184842
            },
            {
                "lon": -79.268661,
                "lat": 41.173447
            },
            {
                "lon": -79.29467,
                "lat": 41.176628
            },
            {
                "lon": -79.326133,
                "lat": 41.181225
            },
            {
                "lon": -79.354174,
                "lat": 41.17774
            },
            {
                "lon": -79.376976,
                "lat": 41.178895
            },
            {
                "lon": -79.425491,
                "lat": 41.192554
            },
            {
                "lon": -79.458466,
                "lat": 41.19618
            },
            {
                "lon": -79.493496,
                "lat": 41.200088
            },
            {
                "lon": -79.521889,
                "lat": 41.183469
            },
            {
                "lon": -79.563482,
                "lat": 41.190537
            },
            {
                "lon": -79.605652,
                "lat": 41.187735
            },
            {
                "lon": -79.641448,
                "lat": 41.194788
            },
            {
                "lon": -79.692499,
                "lat": 41.179302
            },
            {
                "lon": -79.742385,
                "lat": 41.173979
            },
            {
                "lon": -79.820064,
                "lat": 41.196675
            },
            {
                "lon": -79.912886,
                "lat": 41.202195
            },
            {
                "lon": -79.988187,
                "lat": 41.203224
            },
            {
                "lon": -80.084882,
                "lat": 41.202844
            },
            {
                "lon": -80.163447,
                "lat": 41.197638
            },
            {
                "lon": -80.27393,
                "lat": 41.186862
            },
            {
                "lon": -80.36258,
                "lat": 41.185453
            },
            {
                "lon": -80.46232,
                "lat": 41.184658
            },
            {
                "lon": -80.509655,
                "lat": 41.184828
            },
            {
                "lon": -80.538142,
                "lat": 41.177083
            },
            {
                "lon": -80.599806,
                "lat": 41.167725
            },
            {
                "lon": -80.656749,
                "lat": 41.158934
            },
            {
                "lon": -80.682514,
                "lat": 41.148304
            },
            {
                "lon": -80.746003,
                "lat": 41.129446
            },
            {
                "lon": -80.789545,
                "lat": 41.121897
            },
            {
                "lon": -80.840365,
                "lat": 41.114004
            },
            {
                "lon": -80.878754,
                "lat": 41.142564
            },
            {
                "lon": -80.932214,
                "lat": 41.185074
            },
            {
                "lon": -80.957484,
                "lat": 41.220741
            },
            {
                "lon": -80.99983,
                "lat": 41.241362
            },
            {
                "lon": -81.084422,
                "lat": 41.243993
            },
            {
                "lon": -81.138942,
                "lat": 41.242546
            },
            {
                "lon": -81.247868,
                "lat": 41.245809
            },
            {
                "lon": -81.256612,
                "lat": 41.246252
            },
            {
                "lon": -81.306885,
                "lat": 41.248665
            },
            {
                "lon": -81.356166,
                "lat": 41.25516
            },
            {
                "lon": -81.410217,
                "lat": 41.252979
            },
            {
                "lon": -81.485626,
                "lat": 41.257247
            },
            {
                "lon": -81.549205,
                "lat": 41.257813
            },
            {
                "lon": -81.586248,
                "lat": 41.253107
            },
            {
                "lon": -81.624828,
                "lat": 41.272394
            },
            {
                "lon": -81.738345,
                "lat": 41.303827
            },
            {
                "lon": -81.831194,
                "lat": 41.342446
            },
            {
                "lon": -81.93007,
                "lat": 41.367241
            },
            {
                "lon": -81.987243,
                "lat": 41.378365
            },
            {
                "lon": -82.044504,
                "lat": 41.378744
            },
            {
                "lon": -82.078349,
                "lat": 41.386767
            },
            {
                "lon": -82.121332,
                "lat": 41.39156
            },
            {
                "lon": -82.217936,
                "lat": 41.379717
            },
            {
                "lon": -82.286141,
                "lat": 41.35968
            },
            {
                "lon": -82.360065,
                "lat": 41.338457
            },
            {
                "lon": -82.520435,
                "lat": 41.32608
            },
            {
                "lon": -82.611968,
                "lat": 41.323015
            },
            {
                "lon": -82.767876,
                "lat": 41.341354
            },
            {
                "lon": -82.916938,
                "lat": 41.360402
            },
            {
                "lon": -83.056417,
                "lat": 41.389379
            },
            {
                "lon": -83.167913,
                "lat": 41.421275
            },
            {
                "lon": -83.284224,
                "lat": 41.458461
            },
            {
                "lon": -83.358697,
                "lat": 41.485895
            },
            {
                "lon": -83.433163,
                "lat": 41.514657
            },
            {
                "lon": -83.518824,
                "lat": 41.54131
            },
            {
                "lon": -83.596192,
                "lat": 41.575571
            },
            {
                "lon": -83.732499,
                "lat": 41.59142
            },
            {
                "lon": -83.88431,
                "lat": 41.600014
            },
            {
                "lon": -84.011761,
                "lat": 41.598346
            },
            {
                "lon": -84.109488,
                "lat": 41.59066
            },
            {
                "lon": -84.164128,
                "lat": 41.591927
            },
            {
                "lon": -84.303459,
                "lat": 41.591376
            },
            {
                "lon": -84.339914,
                "lat": 41.587734
            },
            {
                "lon": -84.373333,
                "lat": 41.599495
            },
            {
                "lon": -84.498457,
                "lat": 41.607793
            },
            {
                "lon": -84.57139,
                "lat": 41.615974
            },
            {
                "lon": -84.63682,
                "lat": 41.616583
            },
            {
                "lon": -84.691055,
                "lat": 41.622085
            },
            {
                "lon": -84.776284,
                "lat": 41.630374
            },
            {
                "lon": -84.84013,
                "lat": 41.646214
            },
            {
                "lon": -84.883006,
                "lat": 41.684477
            },
            {
                "lon": -84.961712,
                "lat": 41.720637
            },
            {
                "lon": -85.016556,
                "lat": 41.742107
            },
            {
                "lon": -85.097862,
                "lat": 41.750151
            },
            {
                "lon": -85.23021,
                "lat": 41.755378
            },
            {
                "lon": -85.290777,
                "lat": 41.739982
            },
            {
                "lon": -85.367883,
                "lat": 41.748461
            },
            {
                "lon": -85.43512,
                "lat": 41.753794
            },
            {
                "lon": -85.539134,
                "lat": 41.745897
            },
            {
                "lon": -85.620952,
                "lat": 41.751451
            },
            {
                "lon": -85.671218,
                "lat": 41.748006
            },
            {
                "lon": -85.765339,
                "lat": 41.729489
            },
            {
                "lon": -85.813488,
                "lat": 41.735673
            },
            {
                "lon": -85.938184,
                "lat": 41.730344
            },
            {
                "lon": -86.02727,
                "lat": 41.733189
            },
            {
                "lon": -86.110783,
                "lat": 41.733912
            },
            {
                "lon": -86.172267,
                "lat": 41.716874
            },
            {
                "lon": -86.249326,
                "lat": 41.722508
            },
            {
                "lon": -86.305399,
                "lat": 41.72906
            },
            {
                "lon": -86.385345,
                "lat": 41.734179
            },
            {
                "lon": -86.436526,
                "lat": 41.748887
            },
            {
                "lon": -86.462791,
                "lat": 41.755438
            },
            {
                "lon": -86.530444,
                "lat": 41.740661
            },
            {
                "lon": -86.583263,
                "lat": 41.72687
            },
            {
                "lon": -86.633534,
                "lat": 41.699694
            },
            {
                "lon": -86.677252,
                "lat": 41.673801
            },
            {
                "lon": -86.742254,
                "lat": 41.662282
            },
            {
                "lon": -86.798695,
                "lat": 41.626941
            },
            {
                "lon": -86.868644,
                "lat": 41.596784
            },
            {
                "lon": -86.965733,
                "lat": 41.575018
            },
            {
                "lon": -87.055231,
                "lat": 41.574718
            },
            {
                "lon": -87.119001,
                "lat": 41.577363
            },
            {
                "lon": -87.158319,
                "lat": 41.577519
            },
            {
                "lon": -87.203332,
                "lat": 41.585452
            },
            {
                "lon": -87.269758,
                "lat": 41.589896
            },
            {
                "lon": -87.305421,
                "lat": 41.596385
            },
            {
                "lon": -87.342446,
                "lat": 41.606065
            },
            {
                "lon": -87.399749,
                "lat": 41.607088
            },
            {
                "lon": -87.482452,
                "lat": 41.613609
            },
            {
                "lon": -87.503852,
                "lat": 41.632725
            },
            {
                "lon": -87.51598,
                "lat": 41.657142
            },
            {
                "lon": -87.522321,
                "lat": 41.700246
            },
            {
                "lon": -87.548633,
                "lat": 41.722649
            },
            {
                "lon": -87.588163,
                "lat": 41.751579
            },
            {
                "lon": -87.626967,
                "lat": 41.77546
            },
            {
                "lon": -87.630051,
                "lat": 41.813204
            },
            {
                "lon": -87.642298,
                "lat": 41.847489
            },
            {
                "lon": -87.645008,
                "lat": 41.85362
            },
            {
                "lon": -87.63623,
                "lat": 41.875569
            },
            {
                "lon": -87.624351,
                "lat": 41.875562
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
