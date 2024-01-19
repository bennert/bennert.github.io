""" Maak rijschema voor Achilles '95 """
from datetime import timedelta
import os
import requests
import icalendar
from dotenv import load_dotenv

load_dotenv()

def get_google_maps_url(place):
    """ Get google maps url """
    url_maps_place = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?' + \
        'input=' + place + \
        f'&inputtype=textquery&fields=place_id&key={os.getenv("MAPS_API_KEY")}'
    response_place = requests.get(url_maps_place, timeout=10).json()['candidates'][0]['place_id']
    return 'https://www.google.com/maps/search/?api=1&query=Google&query_place_id='+ response_place

def get_google_maps_distance_and_duration(place):
    """ Get google maps distance """
    url_maps_distance = 'https://maps.googleapis.com/maps/api/distancematrix/json?' + \
        'units=metric&origins=51.4281731,5.3850569&destinations=' + \
        place + f'&key={os.getenv("MAPS_API_KEY")}'
    response = requests.get(url_maps_distance, timeout=10).json()
    return response['rows'][0]['elements'][0]['distance']['value'] / 1000, \
        response['rows'][0]['elements'][0]['duration']['value'] / 60

def get_sportlink_calendar():
    """ Get events from sportlink """
    url_sportlink = f'https://data.sportlink.com/ical-team?token={sportlink_token}'
    response = requests.get(url_sportlink, timeout=10)
    content = response.content
    return icalendar.Calendar.from_ical(content)

def get_events_from_calendar():
    """ Get events from calendar """
    events = []
    for event in calendar.walk('VEVENT'):
        summary = event.get('summary')
        start = event.get('dtstart').dt.strftime('%H:%M')
        end = event.get('dtend').dt.strftime('%H:%M')
        location = event.get('location')
        url_map = get_google_maps_url(location)
        location_link = f'[{location}]({url_map})'
        date = event.get('dtstart').dt.strftime('%Y-%m-%d')
        weekday = event.get('dtstart').dt.strftime('%A')
        if base_location in location:
            distance_str = '0'
            duration_str = '0'
            collection_time = (event.get('dtstart').dt - timebefore).strftime('%H:%M')
        else:
            distance, duration = get_google_maps_distance_and_duration(location)

            # calculate colletion time: start - timebefore - time to travel - 5 min
            collection_time = \
                (event.get('dtstart').dt - timebefore \
                - timedelta(minutes=duration) \
                - timedelta(minutes=5)).strftime('%H:%M')
            collection_time = collection_time[:-1] + '0'
            distance_str = f"{distance:.2f}"
            duration_str = f"{duration:.2f}"

        singleevent = [
            date, weekday, summary, collection_time, start, end, location_link,
            distance_str, duration_str]
        events.append(singleevent)
    return events

def get_events_header(language):
    """ Get events header """
    return events_header_list[language].replace("<BASE>", base_location)

assert os.getenv('MAPS_API_KEY'), 'MAPS_API_KEY not set'
assert os.getenv('SPORTLINK_TOKEN_LIST'), 'SPORTLINK_TOKEN_LIST not set'
FILE_PATH_NL = 'docs/Handbal/index.md'
FILE_PATH_EN = 'docs/Handbal/index.en.md'
# Ensure the directories exist
os.makedirs(os.path.dirname(FILE_PATH_NL), exist_ok=True)
os.makedirs(os.path.dirname(FILE_PATH_EN), exist_ok=True)

# Sportlink
sportlink_token_list = os.getenv('SPORTLINK_TOKEN_LIST').split(',')

events_header_list = {
    'en': "| Date | Day | Summary | Time @<BASE> | Start | End | Location | Travel kms " +  \
        "| Travel Minutes |\n",
    'nl': "| Datum | Dag | Samenvatting | Tijd @<BASE> | Start | Einde | Locatie | Reis km " + \
        "| Reis minuten |\n"
}

with open(FILE_PATH_NL, 'w', encoding='utf-8') as file_nl, \
     open(FILE_PATH_EN, 'w', encoding='utf-8') as file_en:
    file_nl.write('# Wedstrijden Achilles \'95\n')
    file_en.write('# Competition Achilles \'95\n')
    for sportlink_token_item in sportlink_token_list:
        team_id = sportlink_token_item.split(':')[0]
        base_location = sportlink_token_item.split(':')[1]
        sportlink_token = sportlink_token_item.split(':')[2]
        print(f'Processing {team_id} @ base: {base_location}')
        # Presence time before game
        timebefore = timedelta(minutes=60)
        calendar = get_sportlink_calendar()
        calendar_events = get_events_from_calendar()
        # Sort events on date
        calendar_events.sort(key=lambda x: x[0])

        file_nl.write(f'\n## Rijschema {team_id}\n\n')
        file_nl.write(get_events_header('nl'))
        file_nl.write('| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n')
        for calendar_event in calendar_events[1:]:
            file_nl.write('| ' + ' | '.join(calendar_event) + ' |\n')

        file_en.write(f'\n## Driving schedule {team_id}\n\n')
        file_en.write(get_events_header('en'))
        file_en.write('| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n')
        for calendar_event in calendar_events[1:]:
            file_en.write('| ' + ' | '.join(calendar_event) + ' |\n')
