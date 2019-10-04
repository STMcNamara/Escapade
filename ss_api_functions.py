"""
This file contains helper functions used to interogate and manipulate the
data received from the RapidAPI skyscanner API. Refer to:
https://rapidapi.com/skyscanner/api/skyscanner-flight-search
"""

import requests, json, csv, string

# Define API header information
headers = {
    'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
    'x-rapidapi-key': "4011c6f5a6mshcd5d2ca5e8bab38p1eb8bcjsn5241ab378907"
    }

def CSVtoDict(csv_input_file):
    """
    GENERAL PURPOSE - Opens a CSV containing data with a single header row and
    returns a list of dictionaries for each row

    Args:
        csv_input_file (.csv file): A .csv file formated with a single header
        row (keys), and any number of rows containing data (values).

    Returns:
        inputDicts (list(of dictionaries)): A list of dictionaries, each with
        keys derived from the header row of the .cvs input.

    Exceptions:
        TODO
    """
    # Open .csv and read each line
    inputFile = open(csv_input_file)
    inputDicts = csv.DictReader(inputFile)

    return inputDicts


def DicttoCSV(dict):
    """
    GENERAL PURPOSE - Reads a list of dictionaries and converts to a
    results.csv file in the dev_area

    Args:
        dict(list(of dictionaries)): A list of dictionaries, each of which must
        have keys that are the same as the list dictionary in the list.

    Returns:
        Creates a .csv file named results.csv in which the first row is the
        dictionary keys, and each following row is the associated values for each
        dictionary in the list.

    Exceptions:
        TODO
    """
    keys = dict[0].keys()
    with open('dev_area/results.csv', 'w') as results:
        dict_writer = csv.DictWriter(results, keys)
        dict_writer.writeheader()
        dict_writer.writerows(dict)


def formatBqUrl(inputDicts):
    """
    Takes a list of dictionaries containing the following required key value
    pairs with the following names: "country", "currency", "locale",
    "originplace","destinationplace","outboundpartialdate". Produces an URL in
    the format required to make a call to the BrowseQuotes API endpoint.

    Refer to:
    https://skyscanner.github.io/slate/#flights-browse-prices

    Args:
        inputDicts (list(of dictionaries)): A list of dictionaries, each containing keys
        required to contruct an URL for the BrowseQuotes API endpoint.

    Returns:
        urlListBq (list(of strings)): A list of strings in the correct URL format to make
        a call to the BrowseQuotes API endpoint.

    Exceptions:
        TODO
    """
    # Confirm all required API inputs are present for BrowseQuotes - TODO

    # For each dict in list build the URL in the format defined here:
    # https://rapidapi.com/skyscanner/api/skyscanner-flight-search?endpoint=5aa1eab3e4b00687d3574279
    urlListBq = []
    for row in inputDicts:
        urlListBq.append("https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/" +
                            row["country"] + "/" +
                            row["currency"] + "/" +
                            row["locale"] + "/" +
                            row["originplace"] + "/" +
                            row["destinationplace"] + "/" +
                            row["outboundpartialdate"] + "/")
    return urlListBq

def BrowseQuotes(urlList):
    """
    Makes multiple calls to the BrowseQuotesAPI function for each query defined
    within a list of query URLs. Returns a list of the individual dictionary
    responses returned from BrowseQuotesAPI.

    Args:
        urlList (list(of strings)): A list of URLs formated as required to to make
        a call to the BrowseQuotes API endpoint. (Refer to function formatBqUrl
        for details).

    Returns:
        results (list(of dictionaries)): A list of dictionaries, each with key value
        pairs as a minimum of: TODO - this may change.

    Exceptions:
        TODO
    """
    results = []
    for url in urlList:
        quote = BrowseQuotesAPI(url, headers)
        results.append(quote)
    return results


def BrowseQuotesAPI(url, headers):
    """
    Makes a call to the Skyscanner API endpoint Browse Quotes to retreive a
    .JSON formated string comprising search results for the the cheapest flight
    for a given query. Each query comprises a single route, and outbound date
    combination. Refer to:
    https://rapidapi.com/skyscanner/api/skyscanner-flight-search

    Args:
        url (string): A URL in the format required to make a call to the
        Skyscanner Browse Quotes API endpoint. Refer to function formatBqUrl
        for details).

        headers (dictionary): A dictionary containing the html headers required
        to be submitted with the API call. This is a global variable within this
        file.

    Returns:
        results (dictionary): Revalant items from the returned .json, formatted
        as a single dictionary with the following keys:
            MinPrice (string): The price of the trip in the requested currency
            Outbound_OriginID (string): Numeric location identifer for origin
            Outbound_DestinationID (string): Numeric location identifer for
                destination
            Outbound_CarrierID (list): A list of numeric identifiers for the
                carrier(s) for the trip
            Outbound_Date (string): Date of the trip
            Outbound_OriginPlace (string): Name of the origin place
            Outbound_DestinationPlace (string): Name of the destination place
            Outbound_CarrierNames (list): A list of the names of the Carriers
                for the trip

    Exceptions:
        TODO
    """
    # Create blank dictionary to store required data
    results = {}
    # Make the API call and receive .json string
    response_string = requests.request("GET", url, headers=headers)
    # Convert .json into Python lists and dictionaries
    response_json = response_string.json()
    # Extract required data into a single dictionary.
    Quotes_list = response_json["Quotes"]
    Places_list = response_json["Places"]
    Carriers_list = response_json["Carriers"]
    results['MinPrice'] = Quotes_list[0]['MinPrice']
    results['Outbound_OriginID'] = Quotes_list[0]['OutboundLeg']['OriginId']
    results['Outbound_DestinationID'] = Quotes_list[0]['OutboundLeg']['DestinationId']
    results['Outbound_CarrierID'] = Quotes_list[0]['OutboundLeg']['CarrierIds']
    results['Outbound_Date'] = Quotes_list[0]['OutboundLeg']['DepartureDate']

    for place in Places_list:
        if place['PlaceId'] == results['Outbound_OriginID']:
            results['Outbound_OriginPlace'] = place['Name']
        elif place['PlaceId'] == results['Outbound_DestinationID']:
            results['Outbound_DestinationPlace'] = place['Name']


    # There may be multiple carriers so requires a lists
    results['Outbound_CarrierNames'] = []
    for carrier in Carriers_list:
        if carrier['CarrierId'] in results['Outbound_CarrierID']:
            results['Outbound_CarrierNames'].append(carrier['Name'])

    return results

def getLocationsAll():
    """
    This is a WIP tool to gather all place names and codes supported by the
    Skyscanner API. There is a bespoke tool available on the parnter API, but on
    RapidAPI free version this must be approximated by a series of simple
    requests (a - z) intended to capture all place.

    Args:
        None

    Returns:
        places (list(of dictionaries)): A list of dictionaries, each of which
        contains Skyscanner place information with the following keys:
        "CountryId", "PlaceName", "CountryName", "PlaceId", "RegionId", "CityId"

    Exceptions:
        TODO
    """
    # Create empty list for places
    places = []
    # Iterate for each letter in alphabet
    for letter in string.ascii_lowercase:
        # Define fixed URL and query parameters
        url =  "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/autosuggest/v1.0/UK/GBP/en-GB/"
        querystring = {"query":letter}
        # Call API and receive string response. Example format in ./dev_area/results_places.txt
        response_string = requests.request("GET", url, headers=headers, params=querystring)
        # Convert to JSON / dictionary
        response_json = response_string.json()
        # Retreive places as list of dictionaries, and append to full list
        places_list_letter = response_json["Places"]
        if places_list_letter not in places:
            places += places_list_letter

    # TODO - currently returns duplicates!!!
    return places

# Test Area
# url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/US/USD/en-US/SFO-sky/JFK-sky/2019-12-01"
# BrowseQuotes(url,headers)
# url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/US/USD/en-US/SFO-sky/JFK-sky/2019-12-02"
# BrowseQuotes(url,headers)
csv_input = "/home/stmcnamara26/GITS/Escapade/dev_area/quoteinput_1.csv"
dict = CSVtoDict(csv_input)
urllist = formatBqUrl(dict)
resultsdict = BrowseQuotes(urllist)
print(resultsdict)
DicttoCSV(resultsdict)
