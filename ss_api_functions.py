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
    """
    # Open .csv and read each line
    inputFile = open(csv_input_file)
    inputDicts = csv.DictReader(inputFile)

    return inputDicts


def DicttoCSV(dict):
    """
    GENERAL PURPOSE - Reads a list of dictionaries and converts to a
    results.csv file in the dev_area
    """
    keys = dict[0].keys()
    with open('dev_area/results.csv', 'w') as results:
        dict_writer = csv.DictWriter(results, keys)
        dict_writer.writeheader()
        dict_writer.writerows(dict)


def formatBqUrl(inputDicts):
    """
    Reads a list of dictionaries containing the the keys "country", "currency",
    "locale", "originplace", "destinationplace" and "outboundpartialdate" and
    formats them as a list of string Urls
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
    Calls BrowseQuotesAPI for each formated URL in a list, returns a list of
    dictionaries.
    """
    results = []
    for url in urlList:
        quote = BrowseQuotesAPI(url, headers)
        results.append(quote)
    print(results)
    return results


def BrowseQuotesAPI(url, headers):
    """
    Takes an individual string url and calls Browse Quotes in skyscanner API.
    Returns a dicionary with min all input data, cheapest price, carrier and
    quote time.
    Note, refer to BrowseQuotesAPIresponses.docx for example formatting
    """
    # Create blank dictionary to store required data
    results = {}
    response_string = requests.request("GET", url, headers=headers)
    response_json = response_string.json()
    Quotes_list = response_json["Quotes"]#
    results['MinPrice'] = Quotes_list[0]['MinPrice']
    results['Outbound_OriginID'] = Quotes_list[0]['OutboundLeg']['OriginId']
    results['Outbound_DestinationID'] = Quotes_list[0]['OutboundLeg']['DestinationId']
    results['Outbound_CarrierID'] = Quotes_list[0]['OutboundLeg']['CarrierIds'][0]
    results['Outbound_Date'] = Quotes_list[0]['OutboundLeg']['DepartureDate']

    return results

def getLocationsAll():
    """
    Generates a list of dictionaries for all airports, by querying List Places
    endpoint one letter at a time.
    Note: This is unnessary on a partner API, as there is an additional endpoint
    for all. Also currently unsure if this will provide ALL places.
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
        places += places_list_letter

    # TODO - currently returns duplicates!!!    
    print(places)
    return places

"""
Test area

# url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/US/USD/en-US/SFO-sky/JFK-sky/2019-12-01"
# BrowseQuotes(url,headers)
# url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/US/USD/en-US/SFO-sky/JFK-sky/2019-12-02"
# BrowseQuotes(url,headers)
csv_input = '.\dev_area\quoteinput_1.csv'
dict = CSVtoDict(csv_input)

urllist = formatBqUrl(dict)
resultsdict = BrowseQuotes(urllist)
print(resultsdict)

DicttoCSV(resultsdict)
"""

places = getLocationsAll()
DicttoCSV(places)
