import datetime
from flask import Flask, request
import requests
import requests_cache
from typing import List


app = Flask(__name__)

@app.route('/', methods=['GET'])
def getPlayitasPrices():
    requests_cache.install_cache('cheapPlayitas', expire_after=3600, )

    args = request.args
    oneMax = args.get("MaxPrice7", default=None, type=int)
    twoMax = args.get("MaxPrice14", default=None, type=int)
    persons = args.get("persons", default=2, type=int)
    sortbydate = args.get("sortbydate", default=False, type=bool)

    airports = []
    airports.append("CPH") if args.get("airportcph", default=False, type=bool) else False
    airports.append("BLL") if args.get("airportbll", default=False, type=bool) else False
    airports.append("AAL") if args.get("airportaal", default=False, type=bool) else False
    airports.append("AAR") if args.get("airportaar", default=False, type=bool) else False

    prices = []
    for airport in airports:
      prices += getPrices( "7", airport, oneMax, persons) if oneMax != None else ""
      prices += getPrices( "14", airport, twoMax, persons) if twoMax != None else ""

    sortedPrices = SortPrices(prices, sortbydate)
    res = PrettyHtmlPrices(sortedPrices)
    return res

def SortPrices(travelPrices, sortbydate):
  travelPrices.sort(key=lambda x: (x.get('Duration'), x.get('CheapestPrice')))
  if(sortbydate):
    travelPrices.sort(key=lambda x: (x.get('Duration'), x.get('Date')))
  return travelPrices

def getPrices(travelDuration, airport, maxPrice, persons):
  date = datetime.datetime.now().date()
  currentMonth = int(date.strftime("%m"))
  currentYear = int(date.strftime("%Y"))

  travelPrices = []
  # hotels = {
  #   "Annexe":"530116",
  #   "Playitas Resort": "160759"
  #   }
  paxAges = createPaxAgesString(persons)

  date = datetime.datetime.now().date()
  currentYear = int(date.strftime("%Y"))
  currentMonth = int(date.strftime("%m"))
  years = [currentYear, currentYear+1]

  for year in years:
    monthStart = 1
    if year == currentYear:
      monthStart = currentMonth
    hotels = getHotelList()
    for hotel in hotels:
      for month in [str(i).zfill(2) for i in range(monthStart, 13)]:
        url = f"https://www.apollorejser.dk/PriceCalendar/Calendar?ProductCategoryCode=FlightAndHotel&DepartureDate={year}-{month}-01&departureAirportCode={airport}&duration={travelDuration}&catalogueItemId={hotel.hotelId}&departureDateRange=31&paxAges={paxAges}"
        r = requests.get(url = url)
        # print(r.from_cache)
        if(r.status_code == 200):
          data = r.json()
          data = removeSoldOutTravels(data)
          data = removeOverLimitPriceTravels(data, maxPrice)
          if(len(data) > 0):
            for travelObj in data:
              travelObj['Airport'] = airport
              travelObj['Duration'] = travelDuration
              travelObj['Hotel'] = hotel.displayName
              travelObj['Link'] = f'https://www.apollorejser.dk/{hotel.hotelUrl}?departureDate={travelObj["Date"][0:10]}&departureAirportCode={airport}&duration={travelDuration}&catalogueItemId={hotel.hotelId}&departureDateRange=31&paxAges={paxAges}'
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


class Hotel:
  displayName: str
  hotelId: str
  hotelUrl: str

  def __init__(self, displayName: str, hotelId: str, hotelUrl: str):
    self.displayName = displayName
    self.hotelId = hotelId
    self.hotelUrl = hotelUrl


def getHotelList() -> List[Hotel]:
  hotels = []
  hotels.append(Hotel("Porto Myrina (Grækenland)", "158862", "graekenland/limnos/hoteller/porto-myrina---powered-by-playitas"))
  hotels.append(Hotel("Playitas Annexe (Fuerteventura)", "530116", "spanien/de-kanariske-oer/fuerteventura/playitas-resort/hoteller/playitas-annexe"))
  hotels.append(Hotel("Playitas Resort (Fuerteventura)", "160759", "spanien/de-kanariske-oer/fuerteventura/playitas-resort/hoteller/playitas-resort"))

  return hotels




def PrettyHtmlPrices(travelPrices):
    args = request.args
    res = f'''
    <html>
    <head>
    <style>
    table {{
      font-family: arial, sans-serif;
      border-collapse: collapse;
      width: 100%;
    }}

    td, th {{
      border: 1px solid #dddddd;
      text-align: left;
      padding: 8px;
    }}

    tr:nth-child(even) {{
      background-color: #dddddd;
    }}

    input[type=number] {{
      width: 100%;
      padding: 12px 20px;
      margin: 8px 0;
      box-sizing: border-box;
    }}

    input[type=number]:focus {{
      border: 3px solid #555;
    }}

    input[type=checkbox] {{
      width: 40px;
      height: 40px;
    }}

    </style>
    </head>
    <body>

    <form action="/">
      <input type="number" name="MaxPrice7" value="{args.get("MaxPrice7", default=None, type=int)}" placeholder="Max Pris 7 Dage"><br>
      <input type="number" name="MaxPrice14" value="{args.get("MaxPrice14", default=None, type=int)}" placeholder="Max Pris 14 Dage"><br>
      <input type="number" name="persons" value="{args.get("persons", default=None, type=int)}" placeholder="Antal Personer (Default: 2)"><br>
      <input type="checkbox" value="true" {"checked" if args.get("airportcph", default=False, type=bool) else ""} name="airportcph"><label>CPH</label>
      <input type="checkbox" value="true" {"checked" if args.get("airportbll", default=False, type=bool) else ""} name="airportbll"><label>BLL</label>
      <input type="checkbox" value="true" {"checked" if args.get("airportaal", default=False, type=bool) else ""} name="airportaal"><label>ALL</label>
      <input type="checkbox" value="true" {"checked" if args.get("airportaar", default=False, type=bool) else ""} name="airportaar"><label>AAR</label> <br><br> 
      <input type="checkbox" value="true" {"checked" if args.get("sortbydate", default=False, type=bool) else ""} name="sortbydate"><label>Sorter på Dato</label> <br><br> 
      <input type="submit" value="Submit">
    </form>

    <table>
      <tr>
        <th>Lufthavn</th>
        <th>Varighed</th>
        <th>Dato</th>
        <th>Pris</th>
        <th>Hotel</th>
        <th>Link</th>
      </tr>
    '''
    for travelPrice in travelPrices:
        res += f"""
        <tr>
          <td>{travelPrice['Airport']}</td>
          <td>{travelPrice['Duration']}</td>
          <td>{travelPrice['Date'][0:10]}</td>
          <td>{travelPrice['CheapestPrice']}</td>
          <td>{travelPrice['Hotel']}</td>
          <td><a href="{travelPrice['Link']}">Link</a></td>
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