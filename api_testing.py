import os
import glob
import ss_api_functions
import datetime
import shutil
import time

# Define the parameters for the test
testCasePath = "./testing/ss_tests/testcases/" # Location of test case files
resultsTopFolder = "./testing/ss_tests/testruns/" # Location of results folder
numTestRuns = 16 # Number of times to repeat the tests
runInterval = 600 # Wait time between test runs in seconds
endPointList =[ss_api_functions.BrowseQuotes] # The API functions to call
# Results folder file size limit - TODO

# Create folder structure to store result in
startTime = datetime.datetime.now()
resultsFolderPath = resultsTopFolder + '/testrun_' + startTime.strftime("%Y-%m-%d_%H'%M'%S" + '/')
copyTestCasesPath = resultsFolderPath + '/testcases/'
os.mkdir(resultsFolderPath)
os.mkdir(copyTestCasesPath)

# Copy all testcases into results folder to preserve history and build test case list
testCases = []
for fileName in os.listdir(testCasePath):
    shutil.copy(testCasePath + fileName, copyTestCasesPath)
    testCases.append(fileName)

# Generate some useful test metadata and display to the user
numEP = len(endPointList) # Number of endpoints being tested
numTestCases = len(testCases) # Number of test cases

print('Commencing testing of {} endpoints using {} testcases. \
All test cases will be run {} number of times with a {} second \
interval between them'.format(numEP,numTestCases,numTestRuns,runInterval))

# Make the results file and log the start of the start time - TODO

# For each test run
runNo = 0
for testRun in range(numTestRuns):
    runNo += 1
    print('Commencing test run {} of {}'.format(runNo,numTestRuns))
    
    # For each enpoint function to be tested
    for endPoint in endPointList:
        print('Testing endpoint {}'.format(endPoint))

        # For each test case
        testNo = 0
        for testCase in testCases:
            testNo += 1
            testCasePath = copyTestCasesPath + testCase
            print('Commencing test case {} ({} of {})'.format(testCase, testNo, numTestCases))

            # Try to call the function and write the results
            try:
                # Make the API call
                inputDicts = ss_api_functions.CSVtoDict(testCasePath)
                resultsJson = endPoint(inputDicts)
                resultsFormatted = ss_api_functions.BrowseQuotesFormatResults(resultsJson)

                # Write the responses to file
                ResultsFileName = "resultsrun_" + str(runNo) + "_" + testCase
                ResultsFilePath = resultsFolderPath + ResultsFileName 
                ss_api_functions.DicttoCSV(resultsFormatted, ResultsFilePath)            
            
            except Exception as e: 
                print(e)
                print('Failed to call and process API, skipping to next test case')

    print('Wating {} seconds before commencing next test run.'.format(runInterval))
    time.sleep(runInterval)

    # For each testcase
        # 

        # Log the start time

        # Make the api call

        # Log the end time
# or each 

# Functionality for doing this more than once with a delay