import os

COWIN_URL = os.getenv('COWIN_URL')
STATES_URL = f'{COWIN_URL}admin/location/states/'
DISTRICTS_URL = f'{COWIN_URL}admin/location/districts/'
CALENDAR_BY_DISTRICT_PUBLIC_URL = f'{COWIN_URL}appointment/sessions/public/calendarByDistrict/'
CALENDAR_BY_DISTRICT_URL = f'{COWIN_URL}appointment/sessions/calendarByDistrict/'
FIND_BY_DISTRICT_URL = f'{COWIN_URL}appointment/sessions/public/findByDistrict'
GOOGLE_GEOCODE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
GMAPS_API_KEY = os.getenv('GCP_API_KEY')

BOTH = 'both'
COVISHIELD = 'covishield'
COVAXIN = 'covaxin'
SPUTNIK = 'sputnik v'
ABOVE_18 = 'above_18'
ABOVE_45 = 'above_45'
ABOVE_18_COWIN = '18'
ABOVE_45_COWIN = '45'
WEBSITE_URL = os.getenv('WEBSITE_URL')
DB_NAME = os.getenv('DB_NAME')

ISSUE_MSG = 'There was an issue with your request, please contact the developers'

NUM_WEEKS = 1

EMAIL_SUBJECT = '%s vaccine slots available at %s - %s!'

EMAIL_BODY = f"""<html>
    <body>
      <p>New vaccine slot available!<br>
        %s in %s on %s
      </p>
      <p>
      Age group: %s
      Vaccine: %s
      </p>
      <p>
      Complete Address: %s<br>
      Pincode %s
      </p>
      <p>
      Cost: %s
      </p>
      <p>
      Slots: %s
      </p>
      
    </body>
      <p>
      To unsubscribe from further notifications, please click here: {WEBSITE_URL}/unsubscribe?email=%s&token=%s
      </p>
      </html>"""

VERIFY_SUBJECT = 'Please verify your email'

VERIFY_EMAIL_BODY = f"""<html>
    <body>
      <p>Please verify your email here: {WEBSITE_URL}/verify_email?email=%s&token=%s
      </p>
    </body>
    </html>"""

TEMPLATE_DATA = f"""{{
    "center_name": "%s",
    "slots": "%s",
    "district_name": "%s",
    "date": "%s",
    "age_group": "%s",
    "vaccine": "%s",
    "address": "%s",
    "pincode": "%s",
    "unsub_endpoint": "%s",
    "capacity": "%s",
    "capacity_dose_1": "%s",
    "capacity_dose_2": "%s",
    "fee_amount": "%s"
}}"""

TEMPLATE_DATA_PINCODE = f"""{{
    "email": "%s",
    "unsub_endpoint": "%s"
}}"""

UNSUB_ENDPOINT = f"{WEBSITE_URL}/unsubscribe?email=%s&token=%s"
