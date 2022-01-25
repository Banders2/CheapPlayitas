from flask import Flask, request
from markupsafe import re
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def getPlayitasPrices():
    args = request.args
    oneMax = args.get("MaxPrice7", default=0, type=int)
    twoMax = args.get("MaxPrice14", default=0, type=int)
    persons = args.get("persons", default=2, type=int)
    prices = []
    if oneMax != 0:
        prices += getPrices("2022", "7", "CPH", oneMax, persons)
        prices += getPrices("2022", "7", "BLL", oneMax, persons)
        prices += getPrices("2023", "7", "CPH", oneMax, persons)
        prices += getPrices("2023", "7", "BLL", oneMax, persons)
    if twoMax != 0:
        prices += getPrices("2022", "14", "CPH", twoMax, persons)
        prices += getPrices("2022", "14", "BLL", twoMax, persons)
        prices += getPrices("2023", "14", "CPH", twoMax, persons)
        prices += getPrices("2023", "14", "BLL", twoMax, persons)

    sortedPrices = SortPrices(prices)
    res = PrettyHtmlPrices(sortedPrices)
    return res

def SortPrices(travelPrices):
  travelPrices.sort(key=lambda x: (x.get('Duration'), x.get('CheapestPrice')))
  return travelPrices

def getPrices(year, travelDuration, airport, maxPrice, persons):
  travelPrices = []
  hotels = {
    "Annexe":"530116",
    "Playitas Resort": "160759"
    }
  paxAges = createPaxAgesString(persons)

  for hotelName,hotelId in hotels.items():
    for month in [str(i).zfill(2) for i in range(1, 13)]:
      url = f"https://www.apollorejser.dk/PriceCalendar/Calendar?ProductCategoryCode=FlightAndHotel&DepartureAirportCode={airport}&DepartureDate={year}-{month}-01&DurationGroupCode={travelDuration}&CatalogueItemId={hotelId}&DepartureDateRange=31&PaxAges={paxAges}"
      r = requests.get(url = url) 
      if(r.status_code == 200):
        data = r.json()
        data = removeSoldOutTravels(data)
        data = removeOverLimitPriceTravels(data, maxPrice)
        if(len(data) > 0):
          for travelObj in data: 
            travelObj['Airport'] = airport
            travelObj['Duration'] = travelDuration
            travelObj['Hotel'] = hotelName
          travelPrices += data
  return travelPrices

def createPaxAgesString(persons):
  personsString = "18"
  for _ in range(1,persons):
    personsString += ",18"
  return personsString

def removeSoldOutTravels(data):
  return list(filter(lambda travelPrice: travelPrice["IsSoldOut"] != True, data))

def removeOverLimitPriceTravels(data, maxPrice):
  return list(filter(lambda travelPrice: travelPrice["CheapestPrice"] <= maxPrice, data))


def PrettyHtmlPrices(travelPrices):
    if len(travelPrices) == 0:
      return "No interesting travels"
    res = """
    <html>
    <head>
    <style>
    table {
      font-family: arial, sans-serif;
      border-collapse: collapse;
      width: 100%;
    }

    td, th {
      border: 1px solid #dddddd;
      text-align: left;
      padding: 8px;
    }

    tr:nth-child(even) {
      background-color: #dddddd;
    }
    </style>
    </head>
    <body>
    <table>
      <tr>
        <th>Airport</th>
        <th>Duration</th>
        <th>Date</th>
        <th>CheapestPrice</th>
        <th>Hotel</th>
      </tr>
    """
    for travelPrice in travelPrices:
        res += f"""
        <tr>
          <td>{travelPrice['Airport']}</td>
          <td>{travelPrice['Duration']}</td>
          <td>{travelPrice['Date'][0:10]}</td>
          <td>{travelPrice['CheapestPrice']}</td>
          <td>{travelPrice['Hotel']}</td>
        </tr>
        """
    res += """
    </table>
    </body>
    </html>
    """
    return res


if __name__ == '__main__':
    app.run()



