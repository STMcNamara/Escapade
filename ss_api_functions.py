import requests, json, csv

# Define API header information
headers = {
    'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
    'x-rapidapi-key': "4011c6f5a6mshcd5d2ca5e8bab38p1eb8bcjsn5241ab378907"
    }

def CSVtoDict(csv_input_file):
    """
    Opens a CSV containing data with a single header row and returns a list of
    dictionaries for each row
    """
    # Open .csv and read each line
    inputFile = open(csv_input_file)
    inputDicts = csv.DictReader(inputFile)

    return inputDicts

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
    Calls BrowseQuotesAPI for each formated URL in a list
    """
    for url in urlList:
        BrowseQuotesAPI(url, headers)


def BrowseQuotesAPI(url, headers):
    """
    Takes an individual string url and calls Browse Quotes in skyscanner API.
    Returns THIS CURRENTLY CALLS WRONG API
    """
    response_string = requests.request("GET", url, headers=headers)
    response_json = response_string.json()
    print(response_json)

"""
Test area
"""
# url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/US/USD/en-US/SFO-sky/JFK-sky/2019-12-01"
# BrowseQuotes(url,headers)
# url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/US/USD/en-US/SFO-sky/JFK-sky/2019-12-02"
# BrowseQuotes(url,headers)
csv_input = '.\dev_area\quoteinput_1.csv'
dict = CSVtoDict(csv_input)

urllist = formatBqUrl(dict)
BrowseQuotes(urllist)
