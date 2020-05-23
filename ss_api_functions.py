"""
This file contains helper functions used to interogate and manipulate the
data received from the RapidAPI skyscanner API. Refer to:
https://rapidapi.com/skyscanner/api/skyscanner-flight-search

At v0.5.1 of the tool, all functionality relating to the Live Search API 
endpoint was removed due to Skyscanner removal from free account privileges.

"""

import requests, json, csv, string, time

# Define API header information
headers = {
    'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
    'x-rapidapi-key': "4011c6f5a6mshcd5d2ca5e8bab38p1eb8bcjsn5241ab378907",
    'content-type': "application/x-www-form-urlencoded"
    }

def CSVtoDict(csv_input_file):
    """
    GENERAL PURPOSE - Opens a CSV containing data with a single header row and
    returns a list of dictionaries for each row containing data

    Args:
        csv_input_file (.csv file): A .csv file formated with a single header
        row (keys), and any number of rows containing data (values).

    Returns:
        inputDicts (list(of dictionaries)): A list of dictionaries, each with
        keys derived from the header row of the .cvs input.
    """
    # Open .csv and read each line
    inputFile = open(csv_input_file)
    inputDicts = csv.DictReader(inputFile)
    # Convert DictRead object to list
    results_list = []
    for row in inputDicts:
        results_list.append(row)
    return results_list


def DicttoCSV(dict,resultsPath):
    """
    GENERAL PURPOSE - Reads a list of dictionaries and CREATES a .csv file with
    the defined name and path.

    Args:
        dict(list(of dictionaries)): A list of dictionaries, each of which must
        have keys that are the same as the first dictionary in the list.

        resultsPath(string): Filepath and file name for the file to be created
        in the fomrat "path/file.csv"

    Returns:
        Creates a .csv file in which the first row is the
        dictionary keys, and each following row is the associated values for each
        dictionary in the list.
    """
    keys = dict[0].keys()
    with open(resultsPath, 'w', newline='') as results:
        dict_writer = csv.DictWriter(results, keys)
        dict_writer.writeheader()
        dict_writer.writerows(dict)

def updateDicttoCSV(dict,resultsPath):
    """
    GENERAL PURPOSE - Reads a list of dictionaries and UPDATES a .csv file with
    the defined name and path.

    Args:
        dict(list(of dictionaries)): A list of dictionaries, each of which must
        have keys that are the same as the first dictionary in the list.

        resultsPath(string): Filepath and file name for the file to be created
        in the fomrat "path/file.csv"

    Returns:
        Creates a .csv file in which the first row is the
        dictionary keys, and each following row is the associated values for each
        dictionary in the list.
    """
    keys = dict[0].keys()
    with open(resultsPath, 'w', newline='') as results:
        dict_writer = csv.DictWriter(results, keys)
        dict_writer.writerows(dict)

def formatBqUrl(inputDict):
    """
    Takes a dictionary containing the following required key value
    pairs with the following names: "country", "currency", "locale",
    "originplace","destinationplace","outboundpartialdate", and the
    optional name "inboundpartialdate". Produces an URL in
    the format required to make a call to the BrowseQuotes API endpoint.

    Refer to:
    https://skyscanner.github.io/slate/#flights-browse-prices

    Args:
        inputDict (dictionary): A dictionary, containing keys
        required to construct an URL for the BrowseQuotes API endpoint.

    Returns:
        urlBq (string): A string in the correct URL format to make
        a call to the BrowseQuotes API endpoint.

    Exceptions:
        TODO 
    """
    # Confirm all required API inputs are present for BrowseQuotes - TODO

    # Contruct the URL in the format defined here:
    # https://rapidapi.com/skyscanner/api/skyscanner-flight-search?endpoint=5aa1eab3e4b00687d3574279
    # Construct URL for Outbound Trip
    urlBq = ("https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/" +
                        inputDict["country"] + "/" +
                        inputDict["currency"] + "/" +
                        inputDict["locale"] + "/" +
                        inputDict["originplace"] + "/" +
                        inputDict["destinationplace"] + "/" +
                        inputDict["outboundpartialdate"] + "/" +
                        inputDict["inboundpartialdate"])
    
    return urlBq

def BrowseQuotesGetData(inputDict):
    """
    Makes a call to the Skyscanner API endpoint Browse Routes to retreive a
    .JSON formated string comprising search results for a given query. 
    Each query comprises a single route, and outbound date combination. 
    Refer to:
    https://rapidapi.com/skyscanner/api/skyscanner-flight-search

    Args:
        inputDict (dictionary): A dictionary, containing keys
        required to construct an URL for the BrowseQuotes API endpoint.

        headers (dictionary): A dictionary containing the html headers required
        to be submitted with the API call. This is a global variable within this
        file.

    Returns:
        response_json (dictionary): A Python formatted json containing
        multiple lists and dictionaries, as recevied from the API endpoint.

    Exceptions:
        TODO - - Need an exception / behaviour if no result returned.

    """
    # Format the request URL for the outbound data
    url = formatBqUrl(inputDict)

    # Make the API call and receive a .json formatted string
    response_string = requests.request("GET", url, headers=headers)

    # Convert .json into Python lists and dictionaries
    response_json = response_string.json()

    return response_json


def BrowseQuotes(inputDictList):
    """
    Makes multiple calls to the BrowseQuotesGetData function for each query defined
    within a list of query URLs. Returns a list of the individual dictionary
    responses returned from BrowseQuotesAPI.

    Args:
        inputDictList (list(of dictionaries)): A list of dictionaries, each of which
        contains the keys required to query to BrowseQuotesAPI endpoint.  (Refer 
        to function formatBqUrl for details).

    Returns:
        results (list(of dictionaries)): A list of dictionaries, each of which has format,
        received from BrowseQuotesGetData function.

    """
    results = []
    for inputDict in inputDictList:
        quote = BrowseQuotesGetData(inputDict)
        results.append(quote)
    
    return results

def BrowseQuotesFormatResults(rawResults):
    """
    Converts a list of raw Browse Quotes API responses into a list of single depth
    dictionaries for parsing to the webapp.

    Args:
        rawResults(list (of dictionaries)): A list of dictionaries, each of which has format,
        received from BrowseQuotesGetData function.

    Returns:
        formattedResultList(list (of dictionaries)): A formatted list of dictionaries,
        each of which has the following keys:
            Outbound_OriginID (string): Numeric location identifer for origin
            Outbound_DestinationID (string): Numeric location identifer for
                destination
            Outbound_CarrierID (list): A list of numeric identifiers for the
                carrier(s) for the outbound leg of the trip
            Outbound_Date (string): Date of the outbound leg of the  trip
            Outbound_OriginPlace (string): Name of the origin place
            Outbound_DestinationPlace (string): Name of the destination place
            Outbound_CarrierNames (list): A list of the names of the Carriers
                for the trip
            Inbound_CarrierID (list): A list of numeric identifiers for the
                carrier(s) for the inbound leg of the trip
            Outbound_Date (string): Date of the inbound leg of the trip
            Inbound_CarrierNames (list): A list of the names of the Carriers
                for the inbound leg of the trip.

    TODO - - Need an exception / behaviour if no result returned. 
    """
    
    formattedResultList = []
    # Try to format results based on valid keys being present in the results
    try:
        for result in rawResults:
            # Extract required data into a single dictionary for outbound leg.
            formattedResult = {}
            Quotes_list = result["Quotes"]
            Places_list = result["Places"]
            Carriers_list = result["Carriers"]
            formattedResult['MinPrice'] = Quotes_list[0]['MinPrice']
            formattedResult['Outbound_OriginID'] = Quotes_list[0]['OutboundLeg']['OriginId']
            formattedResult['Outbound_DestinationID'] = Quotes_list[0]['OutboundLeg']['DestinationId']
            formattedResult['Direct'] = Quotes_list[0]['Direct']
            formattedResult['Outbound_CarrierID'] = Quotes_list[0]['OutboundLeg']['CarrierIds']
            formattedResult['Outbound_Date'] = Quotes_list[0]['OutboundLeg']['DepartureDate']

            for place in Places_list:
                if place['PlaceId'] == formattedResult['Outbound_OriginID']:
                    formattedResult['Outbound_OriginPlace'] = place['Name']
                elif place['PlaceId'] == formattedResult['Outbound_DestinationID']:
                    formattedResult['Outbound_DestinationPlace'] = place['Name']

            # Try to format inbound leg parameters, if present
            formattedResult['Inbound_CarrierID'] = None
            formattedResult['Inbound_Date'] = None
            try:
                formattedResult['Inbound_CarrierID'] = Quotes_list[0]['InboundLeg']['CarrierIds']
                formattedResult['Inbound_Date'] = Quotes_list[0]['InboundLeg']['DepartureDate']
            except:
                pass
        

            # There may be multiple carriers so requires a lists
            formattedResult['Outbound_CarrierNames'] = []
            formattedResult['Inbound_CarrierNames'] = []
            for carrier in Carriers_list:
                if carrier['CarrierId'] in formattedResult['Outbound_CarrierID']:
                    formattedResult['Outbound_CarrierNames'].append(carrier['Name'])
                try:
                    if carrier['CarrierId'] in formattedResult['Inbound_CarrierID']:
                        formattedResult['Inbound_CarrierNames'].append(carrier['Name'])
                except:
                    pass

            # Append to the results list
            formattedResultList.append(formattedResult)
    
    except:
        # TODO - Would be useful to show that results were requested but not received
        pass
    
    return formattedResultList


def validSsAPIResponse(response_json):
    """
    TODO - Requires conversion for Browse Quotes API end point.
    Simply checks whether the response_json input contains the dictionary key
    "Itinaries". Returns a Boolean.
    """
    if "Itinaries" in response_json:
        return True
    else:
        return False


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


if __name__ == "__main__":
    """
    This is a development area to allow API functions to be tested directly without launching
    the main flask app
    """
    print("Running ss_api_functions.py development area")
    
    # Define the path to the testcase folder and list of test cases
    
    testcasefolder = "./testing/ss_tests/testcases/"
    
    
    test_cases = ["./testing/ss_tests/testcases/quoteinput_1.csv",
                "./testing/ss_tests/testcases/quoteinput_10.csv"]

    # Make a results directory with the time and date 
    
    test_number = 1

    for testCase in test_cases:
        print("Testing: " + str(testCase))

        inputDicts = CSVtoDict(testCase)
        resultsJson = BrowseQuotes(inputDicts)
        print(resultsJson)
        resultsFormatted = BrowseQuotesFormatResults(resultsJson)
        print(resultsFormatted)

        # Write responses to file
        resultsPath = "./dev_area/results_" + str(test_number) + ".csv"
        DicttoCSV(resultsFormatted, resultsPath)

        # Increment test number
        test_number += 1

    
