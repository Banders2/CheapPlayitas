import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def sendMail(msg, receiver):
  mail_content = msg
  #The mail addresses and password
  sender_address = 'XXXX@gmail.com'
  sender_pass = 'XXXX'
  receiver_address = receiver
  #Setup the MIME
  message = MIMEMultipart()
  message['From'] = sender_address
  message['To'] = receiver_address
  message['Subject'] = 'Las Playitas - Billig rejse'   #The subject line
  #The body and the attachments for the mail
  message.attach(MIMEText(mail_content, 'plain'))
  #Create SMTP session for sending the mail
  session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
  session.starttls() #enable security
  session.login(sender_address, sender_pass) #login with mail_id and password
  text = message.as_string()
  session.sendmail(sender_address, receiver_address, text)
  session.quit()
  print('Mail Sent')

def createSortedPrices(travelPrices):
  travelPrices.sort(key=lambda x: (x.get('Duration'), x.get('CheapestPrice')))
  # travelPrices.sort(key=lambda x: (x.get('Duration'), x.get('Date')))
  # travelPrices.sort(key=lambda x: x.get('CheapestPrice'))
  text = ""
  for travelPrice in travelPrices:
    text += f"Airport: {travelPrice['Airport']} | Duration: {travelPrice['Duration']:2} | Date: {travelPrice['Date'][0:10]} | CheapestPrice: {travelPrice['CheapestPrice']:5} DKK | Hotel: {travelPrice['Hotel']}\n"
  return text

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



oneWeekPrice = 5000
twoWeekPrice = 9000
prices = []
prices += getPrices("2022", "7", "CPH", oneWeekPrice)
prices += getPrices("2022", "7", "BLL", oneWeekPrice)
prices += getPrices("2022", "14", "CPH", twoWeekPrice)
prices += getPrices("2022", "14", "BLL", twoWeekPrice)
prices += getPrices("2023", "7", "CPH", oneWeekPrice)
prices += getPrices("2023", "7", "BLL", oneWeekPrice)
prices += getPrices("2023", "14", "CPH", twoWeekPrice)
prices += getPrices("2023", "14", "BLL", twoWeekPrice)

if(len(prices) > 0):
  text = createSortedPrices(prices)
  print(text)
  # sendMail(text, Mail)
else:
  print("No interesting travels")