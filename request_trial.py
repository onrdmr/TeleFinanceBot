import requests
from bs4 import BeautifulSoup
import json

# URL of the web page containing the table

url = 'https://gurmefinanswebapi.indata.com.tr/share/db-create'


ALL=["ALL", "https://uzmanpara.milliyet.com.tr/canli-borsa/bist-TUM-hisseleri/"]
BIST_30=["BIST_30", "https://uzmanpara.milliyet.com.tr/canli-borsa/bist-30-hisseleri/"]
BIST_50=["BIST_50", "https://uzmanpara.milliyet.com.tr/canli-borsa/bist-50-hisseleri/"]
BIST_100=["BIST_100", "https://uzmanpara.milliyet.com.tr/canli-borsa/bist-100-hisseleri/"]

def write_stock_names( stocks ):
# Send a GET request to the URL
    response = requests.get(stocks[1])

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        text = response.text
        soup = BeautifulSoup(text, "html.parser")

        # Find the table with the specified ID
        table = soup.select_one("#acik_koyu_yeri > table > tbody")
        table2 = soup.select_one("#acik_koyu_yeri2 > table > tbody")
        table3 = soup.select_one("#acik_koyu_yeri3 > table > tbody")

        for row in table.find_all("tr")[1:]:
            stock_name=row.text.split('\n')[1].strip()
            stocks.append(stock_name)

        for row in table2.find_all("tr")[1:]:
            stock_name = row.text.split("\n")[1].strip()
            stocks.append(stock_name)
        
        for row in table3.find_all("tr")[1:]:
            stock_name = row.text.split("\n")[1].strip()
            stocks.append(stock_name)
        

        file = open(stocks[0], 'w')

        for stock in  stocks[2:]:
            file.write(stock+"\n")

        file.close()
    else:
        print("Failed to retrieve data. Check the URL or your internet connection.")


write_stock_names(ALL)
write_stock_names(BIST_100)
write_stock_names(BIST_50)
write_stock_names(BIST_30)

data = []
for i in range(2, len(ALL)):
    data.append({"name": ALL[i], "type": "ALL"})

headers = {'Content-Type': 'application/json'}
data = json.dumps(data)
response=requests.post(url=url, data=data, headers=headers)

data = []
for i in range(2, len(BIST_100)):
    data.append({"name": BIST_100[i], "type": "BIST_100"})

response=requests.post(url=url, data=data, headers=headers)

data = []
for i in range(2, len(BIST_50)):
    data.append({"name": BIST_50[i], "type": "BIST_50"})

response=requests.post(url=url, data=data, headers=headers)

data = []
for i in range(2, len(BIST_30)):
    data.append({"name": BIST_30[i], "type": "BIST_30"})

response=requests.post(url=url, data=data, headers=headers)



