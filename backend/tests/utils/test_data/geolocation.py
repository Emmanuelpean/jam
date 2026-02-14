"""Mock fixtures for geocoding API calls"""

# Mock geocoding responses based on your test data
MOCK_GEOCODING_RESPONSES = {
    "Cambridge": (
        52.2055314,
        0.1186637,
        {
            "city": "Cambridge",
            "county": "Cambridgeshire",
            "state": "England",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "Oxford": (
        51.7520131,
        -1.2578499,
        {
            "city": "Oxford",
            "county": "Oxfordshire",
            "state": "England",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "United Kingdom": (
        54.7023545,
        -3.2765753,
        {
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "Greater London": (
        51.5074456,
        -0.1277653,
        {
            "city": "Greater London",
            "state": "England",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "London, UK": (
        51.5074456,
        -0.1277653,
        {
            "city": "Greater London",
            "state": "England",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "Manchester, UK": (
        53.4794892,
        -2.2451148,
        {
            "city": "Manchester",
            "state": "England",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "Liverpool": (
        53.4071991,
        -2.99168,
        {
            "city": "Liverpool",
            "state": "England",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "Reading": (
        51.4514953,
        -0.9836342,
        {
            "county": "Reading",
            "state": "England",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "Edinburgh": (
        55.9533456,
        -3.1883749,
        {
            "city": "City of Edinburgh",
            "state": "Scotland",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "Thames Valley": (
        51.7624591,
        -1.1779788,
        {
            "state": "England",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "Polegate": (
        50.8276836,
        0.2446652,
        {
            "town": "Polegate",
            "county": "East Sussex",
            "state": "England",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "Royston": (
        52.0472741,
        -0.0246467,
        {
            "town": "Royston",
            "county": "Hertfordshire",
            "state": "England",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "Hitchin": (
        51.9486943,
        -0.2779124,
        {
            "town": "Hitchin",
            "county": "Hertfordshire",
            "postcode": "SG5 1HP",
            "state": "England",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "Newtownabbey": (
        54.6778816,
        -5.9249199,
        {
            "town": "Newtownabbey",
            "county": "County Antrim",
            "postcode": "BT36 6UN",
            "state": "Northern Ireland",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "Derry": (
        54.9978678,
        -7.3213056,
        {
            "city": "Derry/Londonderry",
            "county": "County Londonderry",
            "postcode": "BT48 6BU",
            "state": "Northern Ireland",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "United States": (
        39.7837304,
        -100.445882,
        {
            "country": "United States",
            "country_code": "us",
        },
    ),
    "USA": (
        39.7837304,
        -100.445882,
        {
            "country": "United States",
            "country_code": "us",
        },
    ),
    "Canada Water, London": (
        51.4979299,
        -0.0498405,
        {
            "suburb": "Rotherhithe",
            "city": "Greater London",
            "postcode": "SE16 7EA",
            "state": "England",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "Weston, Super, Mare": (
        51.3509845,
        -2.9815163,
        {
            "town": "Weston-super-Mare",
            "county": "North Somerset",
            "postcode": "BS23 2AL",
            "state": "England",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "Llantrisant": (
        51.5412874,
        -3.3747857,
        {
            "town": "Llantrisant",
            "county": "Rhondda Cynon Taf",
            "postcode": "CF72 8BU",
            "state": "Wales",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "Bargoed": (
        51.6911236,
        -3.2290284,
        {
            "town": "Bargoed",
            "county": "Caerphilly",
            "state": "Wales",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "Gilfach Goch": (
        51.5935812,
        -3.4713971,
        {
            "village": "Gilfach Goch",
            "county": "Rhondda Cynon Taf",
            "postcode": "CF39 8SR",
            "state": "Wales",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "Bridgend": (
        51.5049859,
        -3.5756674,
        {
            "town": "Bridgend",
            "county": "Bridgend",
            "postcode": "CF31 1DB",
            "state": "Wales",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "Oxfordshire": (
        51.833333,
        -1.25,
        {
            "county": "Oxfordshire",
            "state": "England",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
    "Banbury": (
        52.0601807,
        -1.3402795,
        {
            "town": "Banbury",
            "county": "Oxfordshire",
            "state": "England",
            "country": "United Kingdom",
            "country_code": "gb",
        },
    ),
}


def mock_geocoding_side_effect(query: str):
    """Side effect function for mocking geocoding API calls
    :param query: Location query string
    :return: Tuple of (latitude, longitude, address_dict)
    :raises ValueError: If query is empty or not found"""

    return MOCK_GEOCODING_RESPONSES[query]
