from flask import Flask, request
import requests
import requests_cache
from datetime import timedelta

app = Flask(__name__)

@app.route('/', methods=['GET'])
def getPlayitasPrices():
    requests_cache.install_cache('demo_cache', expire_after=timedelta(hours=1))
    args = request.args
    oneMax = args.get("MaxPrice7", default=None, type=int)
    twoMax = args.get("MaxPrice14", default=None, type=int)
    persons = args.get("persons", default=2, type=int)
    sortbydate = args.get("sortbydate", default=False, type=bool)

    years = []
    years.append("2022") if args.get("year2022", default=False, type=bool) else False
    years.append("2023") if args.get("year2023", default=False, type=bool) else False

    airports = []
    airports.append("CPH") if args.get("airportcph", default=False, type=bool) else False
    airports.append("BLL") if args.get("airportbll", default=False, type=bool) else False
    airports.append("AAL") if args.get("airportaal", default=False, type=bool) else False
    airports.append("AAR") if args.get("airportaar", default=False, type=bool) else False

    prices = []
    for year in years:
      for airport in airports:
        prices += getPrices(year, "7", airport, oneMax, persons) if oneMax != None else ""
        prices += getPrices(year, "14", airport, twoMax, persons) if twoMax != None else ""

    sortedPrices = SortPrices(prices, sortbydate)
    res = PrettyHtmlPrices(sortedPrices)
    return res

def SortPrices(travelPrices, sortbydate):
  travelPrices.sort(key=lambda x: (x.get('Duration'), x.get('CheapestPrice')))
  if(sortbydate):
    travelPrices.sort(key=lambda x: (x.get('Duration'), x.get('Date')))
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
      url = f"https://www.apollorejser.dk/PriceCalendar/Calendar?ProductCategoryCode=FlightAndHotel&DepartureAirportCode={airport}&DepartureDate={year}-{month}-01&Duration={travelDuration}&CatalogueItemId={hotelId}&DepartureDateRange=31&PaxAges={paxAges}"
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

    body{{
        padding:0 20px;
    }}
    .big{{
        font-size: 50px;
    }}

    /* CSS below will force radio/checkbox size be same as font size */
    label{{
        position: relative;
        line-height: 1.4;
    }}
    /* radio */
    input[type=radio]{{
        width: 1em;
        font-size: inherit;
        margin: 0;
        transform: translateX(-9999px);
    }}
    input[type=radio] + label:before{{
        position: absolute;
        content: '';
        left: -1.3em;
        top: 0;
        width: 1em;
        height: 1em;
        margin: 0;
        border:none;
        border-radius: 50%;
        background-color: #bbbbbb;
    }}
    input[type=radio] + label:after{{
        position: absolute;
        content: '';
        left: -1.3em;
        top: 0;
        width: 1em;
        height: 1em;
        margin: 0;
        border: none;
        background-color: white;
        border-radius: 50%;
        transform: scale(0.8);
    }}
    /*checked*/
    input[type=radio]:checked + label:before{{
        position:absolute;
        content:'';
        left: -1.3em;
        top: 0;
        width: 1em;
        height: 1em;
        margin: 0;
        border: none;
        background-color: #3b88fd;
    }}
    input[type=radio]:checked + label:after{{
        position: absolute;
        content: '';
        left: -1.3em;
        top: 0;
        width: 1em;
        height: 1em;
        margin: 0;
        border: none;
        background-color: white;
        border-radius: 50%;
        transform: scale(0.3);
    }}
    /*focused*/
    input[type=radio]:focus + label:before{{
        border: 0.2em solid #8eb9fb;
        margin-top: -0.2em;
        margin-left: -0.2em;
        box-shadow: 0 0 0.3em #3b88fd;
    }}


    /*checkbox/*/
    input[type=checkbox]{{
        width: 1em;
        font-size: inherit;
        margin: 0;
        transform: translateX(-9999px);
    }}
    input[type=checkbox] + label:before{{
        position: absolute;
        content: '';
        left: -1.3em;
        top: 0;
        width: 1em;
        height: 1em;
        margin: 0;
        border:none;
        border-radius: 10%;
        background-color: #bbbbbb;
    }}
    input[type=checkbox] + label:after{{
        position: absolute;
        content: '';
        left: -1.3em;
        top: 0;
        width: 1em;
        height: 1em;
        margin: 0;
        border: none;
        background-color: white;
        border-radius: 10%;
        transform: scale(0.8);
    }}
    /*checked*/
    input[type=checkbox]:checked + label:before{{
        position:absolute;
        content:'';
        left: -1.3em;
        top: 0;
        width: 1em;
        height: 1em;
        margin: 0;
        border: none;
        background-color: #3b88fd;
    }}
    input[type=checkbox]:checked + label:after{{
        position: absolute;
        content: "\2713";
        left: -1.3em;
        top: 0;
        width: 1em;
        height: 1em;
        margin: 0;
        border: none;
        background-color: #3b88fd;
        border-radius: 10%;
        color: white;
        text-align: center;
        line-height: 1;
    }}
    /*focused*/
    input[type=checkbox]:focus + label:before{{
        border: 0.1em solid #8eb9fb;
        margin-top: -0.1em;
        margin-left: -0.1em;
        box-shadow: 0 0 0.2em #3b88fd;
    }}

    </style>
    </head>
    <body>
    <div class="big">
      <form action="/">
        <input type="number" name="MaxPrice7" value="{args.get("MaxPrice7", default=None, type=int)}" placeholder="Max Pris 7 Dage"><br>
        <input type="number" name="MaxPrice14" value="{args.get("MaxPrice14", default=None, type=int)}" placeholder="Max Pris 14 Dage"><br>
        <input type="number" name="persons" value="{args.get("persons", default=None, type=int)}" placeholder="Antal Personer (Default: 2)"><br>
        <input type="checkbox" value="true" {"checked" if args.get("year2022", default=False, type=bool) else ""} name="year2022"><label>2022</label> 
        <input type="checkbox" value="true" {"checked" if args.get("year2023", default=False, type=bool) else ""} name="year2023"><label>2023</label> <br><br> 
        <input type="checkbox" value="true" {"checked" if args.get("airportcph", default=False, type=bool) else ""} name="airportcph"><label>CPH</label>
        <input type="checkbox" value="true" {"checked" if args.get("airportbll", default=False, type=bool) else ""} name="airportbll"><label>BLL</label>
        <input type="checkbox" value="true" {"checked" if args.get("airportaal", default=False, type=bool) else ""} name="airportaal"><label>ALL</label>
        <input type="checkbox" value="true" {"checked" if args.get("airportaar", default=False, type=bool) else ""} name="airportaar"><label>AAR</label> <br><br> 
        <input type="checkbox" value="true" {"checked" if args.get("sortbydate", default=False, type=bool) else ""} name="sortbydate"><label>Sorter på Dato</label> <br><br> 
        <input type="submit" value="Submit">
      </form>
    </div>
    <table>
      <tr>
        <th>Lufthavn</th>
        <th>Varighed</th>
        <th>Dato</th>
        <th>Pris</th>
        <th>Hotel</th>
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