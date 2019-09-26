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
            return None  # Nob hasnt given us their timetable yet
        rawCal = urllib.request.urlopen(url)  # Try and download the timetable's ical
        cal = Calendar.from_ical(rawCal.read())  # Parse the ical
        events = []  # create a list of events

        for component in cal.walk():  # for "thing" in the cal
            if component.name == "VEVENT":  # if its an event
                description = component.get('description').split("\n")  # get all its information
                location = component.get('location')  # unused location data because description has it more reliably
                startdt = component.get('dtstart').dt  # start date/time
                enddt = component.get('dtend').dt  # end date/time

                module = "Undefined"
                room = "Undefined"
                type = "Undefined"

                for item in description:
                    item = str(item)
                    if "MODULE TITLE:" in item:  # get the modules name
                        module = item.replace("MODULE TITLE: ", "")
                    if "ROOM(S):" in item:  # get the room name
                        room = item.replace("ROOM(S): ", "")
                    if "EVENT TYPE:" in item:  # is it a lecture? workshop? seminar?
                        type = item.replace("EVENT TYPE: ", "")
                date = "{:02d}/{:02d}".format(startdt.day, startdt.month)
                timeFormatted = "{Date}-{hour:02d}:{minute:02d}".format(Date=date, hour=startdt.hour+1,
                                                                        minute=startdt.minute)
                endFormatted = "{hour:02d}:{minute:02d}".format(hour=enddt.hour+1, minute=enddt.minute)
                event = Event()  # create an event object
                event.module = module
                event.Ftime = timeFormatted
                event.date = startdt
                event.end = endFormatted
                event.type = type
                event.room = room
                if len(events) != 0:  # put the event, in order, in the list of events
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
        """Outputs a nicely formatted human readable piece of html code for email"""
        if events is None:  # nob didnt share their timetable
            return "Your target has chosen not to share their timetable, sorry"
        text = ""  # the string to be outputted
        lastDate = None  # the last date processed, used to split days with ==========
        for event in events:
            if datetime.now(timezone.utc) <= event.date <= (datetime.now(timezone.utc) + timedelta(days=8)):  # grab the next 7days of timetables (7+1 because datetime is weird)
                # sexy formatting
                TempText = ("||{t}->{e} || {type:<9} || {r:<7} ||<br>".format(t=event.Ftime, e=event.end, type=event.type.lower().capitalize() , r=event.room))
                TempDate = TempText[:5]  # get the date of the event
                if TempDate != lastDate:  # if the last event and this event are on different days
                    text += "="*len(TempText.replace("<br>", "")) + "<br>"  # split them with ======
                    lastDate = TempDate
                text += TempText  # add the nicely formatted string

        return text