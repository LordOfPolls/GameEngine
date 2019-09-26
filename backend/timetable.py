import urllib.request
from icalendar import Calendar, Event
from datetime import datetime, timezone, timedelta
from pytz import UTC # timezone
import pprint
from operator import attrgetter


pprint = pprint.pprint



class Event:
    module = None
    type = None
    room = None
    date = None
    end = None
    Ftime = None

class Timetable:
    @staticmethod
    def TDecode(url):
        """Creates a list of event objects based on a ical url"""
        if url is None:
            return None
        rawCal = urllib.request.urlopen(url)
        cal = Calendar.from_ical(rawCal.read())
        events = []

        for component in cal.walk():
            if component.name == "VEVENT":
                description = component.get('description').split("\n")
                location = component.get('location')
                startdt = component.get('dtstart').dt
                enddt = component.get('dtend').dt

                module = "Undefined"
                room = "Undefined"
                type = "Undefined"

                for item in description:
                    item = str(item)
                    if "MODULE TITLE:" in item:
                        module = item.replace("MODULE TITLE: ", "")
                    if "ROOM(S):" in item:
                        room = item.replace("ROOM(S): ", "")
                    if "EVENT TYPE:" in item:
                        type = item.replace("EVENT TYPE: ", "")
                date = "{:02d}/{:02d}".format(startdt.day, startdt.month)
                timeFormatted = "{Date}-{hour:02d}:{minute:02d}".format(Date=date, hour=startdt.hour+1,
                                                                        minute=startdt.minute)
                endFormatted = "{hour:02d}:{minute:02d}".format(hour=enddt.hour+1, minute=enddt.minute)
                event = Event()
                event.module = module
                event.Ftime = timeFormatted
                event.date = startdt
                event.end = endFormatted
                event.type = type
                event.room = room
                if len(events) != 0:
                    for i in range(len(events)):
                        if event.date < events[i].date:
                            events.insert(i, event)
                            break
                        if i == len(events)-1:
                            events.append(event)
                else:
                    events.append(event)
        return events

    @staticmethod
    def next7(events):
        if events is None:
            return "Your target has chosen not to share their timetable, sorry"
        text = ""
        lastDate = None
        for event in events:
            if datetime.now(timezone.utc) <= event.date <= (datetime.now(timezone.utc) + timedelta(days=8)):
                TempText = ("||{t}->{e} || {type:<9} || {r:<7} ||<br>".format(t=event.Ftime, e=event.end, type=event.type.lower().capitalize() , r=event.room))
                TempDate = TempText[:5]
                if TempDate != lastDate:
                    text += "="*len(TempText.replace("<br>", "")) + "<br>"
                    lastDate = TempDate
                text += TempText

        return text