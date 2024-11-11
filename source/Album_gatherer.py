import datetime
import os
import csv
import requests
import bs4
import random
import time

from collections import defaultdict
from fp.fp import FreeProxy


'''proxy = FreeProxy(country_id=['BR'], rand=True).get()


proxies = {
    'http': proxy,
    'https': proxy,
}
'''


# Function to generate all the dates from start_date to end_date by week
def generate_dates(start_date, end_date):
    current_date = start_date
    while current_date >= end_date:
        yield current_date.strftime('%Y%m%d')
        current_date -= datetime.timedelta(days=7)

# Function to write data to a CSV file, modified to accept year and month
def writeData(data, year, month):
    directory = "data_albums"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Modify the file path to include the year and month and change the extension to .csv
    with open(f"{directory}/top_albums_{year}_{month}.csv", "a", newline='') as file:
        writer = csv.writer(file)
        # Write the header if the file is newly created or empty
        if file.tell() == 0:
            writer.writerow(["Date", "Artist", "Album"])
        writer.writerows(data)


# Function to log the completion of a year
def logYearCompletion(year):
    with open("years_completed.txt", "a") as log_file:
        log_file.write(f"{year} completed\n")
    print(f"{year} completed")


def getAllAlbums(dates):
    albums_by_year = defaultdict(lambda: defaultdict(list))
    current_year = None

    for date in dates:
        year = date[:4]
        month = date[4:6]

        # Detect year change
        if year != current_year and current_year is not None:
            # Write data of each month for the previous year to separate CSV files
            for m, albums in albums_by_year[current_year].items():
                writeData(albums, current_year, m)
            albums_by_year[current_year].clear()  # Clear data after writing
            logYearCompletion(current_year)

        # Fetch albums for the given date
        url = f'https://www.officialcharts.com/charts/albums-chart/{date}/7502/'
        albums = getAlbums(url)

        
        # Store data by month within the year
        for album in albums:
            albums_by_year[year][month].append([date, *album])

        current_year = year  # Update current year

        # Sleep for a random interval between calls
        sleep_time = random.uniform(1, 3)
        time.sleep(sleep_time)

    # Write data for the last year after finishing the loop
    if current_year and albums_by_year[current_year]:
        for m, albums in albums_by_year[current_year].items():
            writeData(albums, current_year, m)
        logYearCompletion(current_year)

def writeData(data, year, month):
    directory = "data_albums"
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(f"{directory}/top_albums_{year}_{month}.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Artist", "Album"])  # Writing header
        writer.writerows(data)




# Main function to get albums and write data
def getAlbums(url):
    all_albums = []

    print(f'Getting Page {url}')
    req = requests.get(url)#, proxies=proxies)
    req.raise_for_status()

    soup = bs4.BeautifulSoup(req.text, "lxml")

    # Here, you would use the actual method to find the date.
    # This is a placeholder example where I'm using the URL to extract the date.
    # You would need to replace this with the correct extraction method.
    date = url.split('/')[-2]  # Example: '20240315' from the URL

    # Assuming the artist and album information is within <div class="chart-item"> as shown in your HTML snippet
    chart_items = soup.find_all("div", class_="chart-item")
    for item in chart_items:
        artist = item.find("a", class_="chart-artist").get_text(strip=True) if item.find("a", class_="chart-artist") else 'Unknown Artist'
        album = item.find("a", class_="chart-name").get_text(strip=True) if item.find("a", class_="chart-name") else 'Unknown Album'

        # Append the album info to allalbums. This needs to be matched with your actual data structure
        all_albums.append([date, artist, album])


    return all_albums





# Start and end dates
start_date = datetime.datetime(1979, 12, 28)   #19791228     2024, 3, 15
end_date = datetime.datetime(1961, 7, 2)
#end_date = datetime.datetime(2024, 2, 16)
dates = generate_dates(start_date, end_date)



getAllAlbums(dates)

