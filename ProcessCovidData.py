import uk_covid19 as cv
import pandas as pd
import numpy as np

from datetime import date, datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def ProcessData(filters):

# Get data from API. (See https://coronavirus.data.gov.uk/developers-guide#structure-metrics)
    dataStructure = {   
        "date": "date", 
        "areaName": "areaName", 
        "newCases": "newCasesBySpecimenDate",  
        "newDeaths": "newDeathsByDeathDate",
    } 

    objCV19 = cv.Cov19API(filters=filters, structure=dataStructure) 

    apiResult = objCV19.get_dataframe()

# Remove dates older than 62 days ago and the newest few depending on time of day.

    earliestDate = date.today() - timedelta(days=62)
    earliestDate = earliestDate.strftime('%Y-%m-%d')

    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")

    if current_time < "17:00:00":
        timeDeltaDays = 2
    else:
        timeDeltaDays = 1

    latestDate = date.today() - timedelta(days=timeDeltaDays)
    latestDate = latestDate.strftime('%Y-%m-%d')

    df = apiResult

    df = df[(df["date"] >= earliestDate) & (df["date"] < latestDate)]

    df = df.sort_values(by="date")

# Calculate 7 day rolling averages.
    df['newCases_SMA_7'] = df["newCases"].rolling(window=7).mean()
    df['newDeaths_SMA_7'] = df["newDeaths"].rolling(window=7).mean()

# Create figure.
    fig = plt.figure(figsize=[15,12])
    fig.set_grid = True
    ax1 = fig.add_subplot(2,1,1)
    ax2 = fig.add_subplot(2,1,2)

    locator = mdates.DayLocator(interval = 7)

    ax1.set_title("Daily Cases")
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Cases')

    ax2.set_title("Daily Deaths")
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Deaths')

    ax1.xaxis.set_major_locator(locator)
    ax2.xaxis.set_major_locator(locator)

    ax1.plot(df["date"], df["newCases"], label="New Cases")
    ax1.plot(df["date"], df["newCases_SMA_7"], label="7 Day Average of New Cases")
    ax1.legend(loc=2)

    ax2.plot(df["date"], df["newDeaths"], label="New Deaths")
    ax2.plot(df["date"], df["newDeaths_SMA_7"], label="7 Day Average of New Deaths")
    ax2.legend(loc=2)

# Return the dataframe and figure.

    return df, fig