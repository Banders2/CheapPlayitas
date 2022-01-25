from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def getPlayitasPrices():
    args = request.args
    oneMax = args.get("MaxPrice7", default=0, type=int)
    twoMax = args.get("MaxPrice14", default=0, type=int)
    prices = []
    if oneMax != 0:
        prices += getPrices("2022", "7", "CPH", oneMax)
        prices += getPrices("2022", "7", "BLL", oneMax)
        prices += getPrices("2023", "7", "CPH", oneMax)
        prices += getPrices("2023", "7", "BLL", oneMax)
    if twoMax != 0:
        prices += getPrices("2022", "14", "CPH", twoMax)
        prices += getPrices("2022", "14", "BLL", twoMax)
        prices += getPrices("2023", "14", "CPH", twoMax)
        prices += getPrices("2023", "14", "BLL", twoMax)

    sortedPrices = SortPrices(prices)
    res = PrettyStringPrices(sortedPrices)
    return res

def PrettyStringPrices(travelPrices):
    if len(travelPrices) == 0:
      return "No interesting travels"
    res = ""
    for travelPrice in travelPrices:
        res += f"Airport: {travelPrice['Airport']} | Duration: {travelPrice['Duration']:2} | Date: {travelPrice['Date'][0:10]} | CheapestPrice: {travelPrice['CheapestPrice']:5} DKK | Hotel: {travelPrice['Hotel']}<br>"
    return res

def SortPrices(travelPrices):
  travelPrices.sort(key=lambda x: (x.get('Duration'), x.get('CheapestPrice')))
  return travelPrices

def getPrices(year, travelDuration, airport, maxPrice):
  travelPrices = []
  hotels = {
    "Annexe":"530116",
    "Playitas Resort": "160759"
    }
  for hotelName,hotelId in hotels.items():
    for month in [str(i).zfill(2) for i in range(1, 13)]:
      url = f"https://www.apollorejser.dk/PriceCalendar/Calendar?ProductCategoryCode=FlightAndHotel&DepartureAirportCode={airport}&DepartureDate={year}-{month}-01&DurationGroupCode={travelDuration}&CatalogueItemId={hotelId}&DepartureDateRange=31&PaxAges=18,18"
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

def removeSoldOutTravels(data):
  return list(filter(lambda travelPrice: travelPrice["IsSoldOut"] != True, data))

def removeOverLimitPriceTravels(data, maxPrice):
  return list(filter(lambda travelPrice: travelPrice["CheapestPrice"] <= maxPrice, data))

if __name__ == '__main__':
    app.run()