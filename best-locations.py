from selenium import webdriver
import pandas as pd

def initializeWebDriver():

    # Location of the Chrome Driver in my system.
    # This should be changed according to your system.
    pathToChromeDriver = '/Users/SRIRAM VETURI/Desktop/chromedriver_win32/chromedriver.exe'
    driver = webdriver.Chrome(executable_path=pathToChromeDriver)
    return driver


def locations():

    # Initializing our Web Driver
    browser = initializeWebDriver()
    # Site to be scraped for data
    browser.get('https://www.coastalliving.com/travel/top-10/tripadvisor-best-summer-destinations')
    # For the below line, you double quotes!
    # Using single quotes would give you some error.
    locationsList = browser.find_elements_by_xpath("//div[@class='padded']/h2/a")
    locationsInfo = browser.find_elements_by_xpath("//div[@class='padded']/p")
    datasetOne = []
    datasetTwo = []
    datasetThree = []

    # Fetching information
    for loc in locationsList:
        entries = (loc.text.encode('ascii', 'replace'), loc.get_attribute('href').encode('ascii', 'replace'))
        datasetOne.append(entries)

    # Fetching information
    # Some specific entries(like the number 23) based on the website's structure
    for info in range(4, len(locationsInfo)):
        if info > 23:
            break
        else:
            if info % 2 == 0:
                information = (locationsInfo[info].text.encode('ascii','replace'))
                datasetTwo.append(information)
            else:
                offer = (locationsInfo[info].text.encode('ascii','ignore'))
                datasetThree.append(offer)

    return datasetOne, datasetTwo, datasetThree

def dataFileGeneration(listData, infoData, offerData):

    dfOne = pd.DataFrame(listData, columns=['PLACES', 'LINKS FOR MORE INFORMATION'])
    dfTwo = pd.DataFrame(infoData, columns=['AVERAGE WEEKLY EXPENSE PER PERSON'])
    dfThree = pd.DataFrame(offerData, columns=['BEST DEALS SUGGESTION'])

    # Use hyperlinks in dataframes
    def make_clickable(val):
        return '<a href="{}">{}</a>'.format(val, val)

    # Processing 'PLACES' column
    for x in dfOne['PLACES']:
        byteStream = str(x)
        new_x = byteStream[2:-1]
        dfOne.replace(x, new_x, inplace=True)

    # Processing 'LINKS FOR MORE INFORMATION' column
    for x in dfOne['LINKS FOR MORE INFORMATION']:
        byteStream = str(x)
        new_x = byteStream[2:-1]
        dfOne.replace(x, new_x, inplace=True)

    # Processing 'AVERAGE WEEKLY EXPENSE PER PERSON' column
    for x in dfTwo['AVERAGE WEEKLY EXPENSE PER PERSON']:
        byteStream = str(x)
        new_x = byteStream[39:-1]
        dfTwo.replace(x, new_x, inplace=True)

    strToBeDeletedList = []
    finalByteStreamlist = []
    bestTime = pd.DataFrame(columns=['BEST TIME TO VISIT'])
    bestDeal = pd.DataFrame(columns=['BEST SAVINGS DEAL'])

    # Processing 'BEST DEALS SUGGESTION' column
    for x in dfThree['BEST DEALS SUGGESTION']:
        byteStream = str(x)
        clearedByteStream = byteStream.replace("Least expensive summer week to go, and the cost: ", "")
        ind = clearedByteStream.index('$')
        strToBeDeleted = clearedByteStream[ind-2:]
        finalByteStream = clearedByteStream.replace(strToBeDeleted, "")
        bestTimeVisit = strToBeDeleted[2:-1]
        strToBeDeletedList.append(bestTimeVisit)
        bestDealVisit = finalByteStream[2:]
        finalByteStreamlist.append(bestDealVisit)

    time = pd.Series(strToBeDeletedList)
    deal = pd.Series(finalByteStreamlist)
    bestTime['BEST TIME TO VISIT'] = deal.values
    bestDeal['BEST SAVINGS DEAL'] = time.values

    # Join all the individual dataframes to a final dataframe
    df = pd.DataFrame()
    df = dfOne.join(dfTwo.join(bestTime.join(bestDeal, lsuffix=bestTime, rsuffix=bestDeal), lsuffix=dfTwo, rsuffix=bestTime), lsuffix=dfOne, rsuffix=dfTwo)
    return df

# Main Function
if __name__ == "__main__":
    listData, infoData, offerData = locations()
    df = dataFileGeneration(listData, infoData, offerData)
    df.to_csv('best_locations.csv')
