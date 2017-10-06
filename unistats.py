# Unistats API Parser
import requests
import json

# opens the file containing the apikey. a default example is given.
with open("apikey.json", "r") as apiKeyFile:
    APIKEY = json.load(apiKeyFile)[0]["unistats"]

# Library functions
def universities(query):
    baseURL = "http://data.unistats.ac.uk/api/v4/KIS/Institutions.JSON?pageIndex={0}&pageSize=100"
    pgN = 0
    URL = baseURL.format(pgN)
    result = []
    USUniResult = requests.get(URL, auth=(APIKEY, 'pass')).json()
    while len(USUniResult) == 100:
        for uni in USUniResult:
            if query.lower() in uni["Name"].lower():
                result.append( {"name": uni["Name"], "prn": uni["UKPRN"]} )
        pgN += 1
        URL = baseURL.format(pgN)
        USUniResult = requests.get(URL, auth=(APIKEY, 'pass')).json()
    else:
        if len(USUniResult) > 0: 
            for uni in USUniResult:
                if query.lower() in uni["Name"].lower():
                    result.append( {"name": uni["Name"], "prn": uni["UKPRN"]} )
        print(result)
        return result

def search(query, uniList):
    # searches the university list for the university name provided, and returns the list of results
    result = []
    for uni in uniList:
        if query.lower() in uni["name"].lower():
            result.append( {"name": uni["name"], "prn": uni["UKPRN"]} )
    return result

def courses(query, prn):
    # browses the unistats api searching for the coursename provided in the arguments as query. prn is the universities' unique id.
    baseURL = "http://data.unistats.ac.uk/api/v4/KIS/Institution/{0}/Courses.JSON?pageIndex={1}&pageSize=100"
    # constructs the url with the prn, and page number 0 for the initial request.
    URL = baseURL.format(prn, 0)
    USCoursesResult = requests.get(URL, auth=(APIKEY, 'pass')).json()
    # gets the length of the first page for comparison, typically this is pageSize.
    initialLength = len(USCoursesResult)
    # forms the result variable which will contain all the search resul;ts
    result = []
    pgN = 1
    # goes through every page of courses seeing if the query is within the title. initialLength is specified instead of pageSize as certain universities provide less than 100 courses (see: imperial college london)
    while len(USCoursesResult) == initialLength:
        for course in USCoursesResult:
            if query.lower() in course["Title"].lower():
                # all the course information required to allow the user to pick a choice, and to get the course information.
                result.append({"title": course["Title"], "KisCourseId": course["KisCourseId"], "KisMode": course["KisMode"]})
        # appends the page number by 1.
        URL = baseURL.format(prn, pgN)
        pgN += 1
        # gets the next page.
        USCoursesResult = requests.get(URL, auth=(APIKEY, 'pass')).json()
    else:
        if len(USCoursesResult) > 0:
            for course in USCoursesResult:
                if query.lower() in course["Title"].lower():
                    # all the course information required to allow the user to pick a choice, and to get the course information.
                    result.append({"title": course["Title"], "KisCourseId": course["KisCourseId"], "KisMode": course["KisMode"]})
        return result

# returns the statistics of the course requested.
def courseStatistics(prn, KisCourseId, KisMode):
    URL = "http://data.unistats.ac.uk/api/v4/KIS/Institution/{0}/Course/{1}/{2}/Statistics.JSON".format(prn, KisCourseId, KisMode)
    return requests.get(URL, auth=(APIKEY, 'pass')).json()

# Program function
def searchParser(result):
    # returns the result of the search performed on the university list, and allows the user to pick one.
    if len(result) > 1:
        id = 0
        # outputs a user friendly version of the results list
        for uni in result:
            print(id, uni["name"])
            id += 1
        chosenID = int(input("Choose your university: "))
        # checks the given ID is within the bounds of the list
        while chosenID > len(result)-1 or chosenID < 0:
            print("Error: Number out of range")
            chosenID = int(input("Choose your university: "))
        else:
            # outputs the given uni's prn.
           return result[chosenID]["prn"]
    elif len(result) == 1:
        return result[0]["prn"]
    else:
        # if there no university, return false.
        return False


def courseParser(result):
    # similar to searchParser()
    if len(result) > 1:
        id = 0
        for course in result:
            print(id, course["title"], "|", course["KisCourseId"], "|", course["KisMode"])
            id += 1
        chosenID = int(input("Choose your course: "))
        while chosenID > len(result)-1 or chosenID < 0:
            print("Error: Number out of range")
            chosenID = int(input("Choose your course: "))
        else:
           return result[chosenID]
    elif len(result) == 1:
        return result[0]
    else:
        return False

def courseStatisticsParser(stats):
    # parses each stat requirement, and outputs a certain statistic from each.
    result = {}
    for stat in stats:
        if stat["Code"] == "COMMON":
            result["percentageLike"] = stat["Details"][0]["Value"]
        if stat["Code"] == "EMPLOYMENT":
            result["percentageInEmployment"] = stat["Details"][0]["Value"]
        if stat["Code"] == "JOBTYPE":
            result["percentageProfessional"] = stat["Details"][0]["Value"]
        if stat["Code"] == "SALARY":
            result["medSalary"] = stat["Details"][4]["Value"]
    return result

# loads the university and allows the user to search the unistats database.
uniList = loadUniList("ukrlp.json")
UKPRN = False
while UKPRN == False:
    unichoice = input("Search University: ")
    UKPRN = searchParser(universities(unichoice))
    if UKPRN == False:
        print("No university found with that name.")
print("UKPRN:", UKPRN)
courseinfo = False
while courseinfo == False:
    coursechoice = input("Search course: ")
    courseinfo = courseParser(courses(coursechoice, UKPRN))    
    if courseinfo == False:
        print("No course found with that name.")
coursestats = print(courseStatisticsParser(courseStatistics(UKPRN, courseinfo["KisCourseId"], courseinfo["KisMode"])))