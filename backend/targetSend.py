import smtplib
import datetime
import random
import os
import getpass
from .formatters import formatters
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

s = smtplib.SMTP(host="smtp.gmail.com", port=587)
s.starttls()

emailTemplateLocation = "backend/Emailtemplates"
if not os.path.isdir(emailTemplateLocation):
    print("Email Templates Folder Not Found")
    os.mkdir(emailTemplateLocation)

class SMEmail:
    def __init__(self):
        self.loggedIn = False

    @staticmethod
    def greetingGen():
        """Generates a greeting"""
        greetings = ["Hello,", "Hi,", "Hi there!", "Greetings,", "Top of the evenin to ya,", "Boo!"]
        return random.choice(greetings)

    def sendEmails(self, email):
        """Sends the emails, after making you log in"""
        if not self.loggedIn:  # if they havent logged in yet
            os.system("cls")
            while not self.loggedIn:
                emailAddr = input("Email: ")
                password = getpass.getpass()  # hide their password entry
                try:
                    s.login(emailAddr, password)  # try and login
                except smtplib.SMTPAuthenticationError:
                    os.system("cls")
                    print("{}Login Failed{}".format(formatters.red, formatters.default))
                finally:  # if successful login with no errors
                    self.loggedIn = True
                    os.system("cls")
                    print("{}Logged in as {}!{}".format(formatters.green, emailAddr, formatters.default))
        print("Sending email to", email['To'])  # user output
        s.send_message(email)  # send


    @staticmethod
    def assembleEmail(html, to, subject="Your Target For {}/{}".format(datetime.datetime.now().day, datetime.datetime.now().month)):
        """Combines all the components of an email, and puts it in an object"""
        msg = MIMEMultipart()
        msg['From'] = "lincolnassassin@lincolnsu.com"
        if "None" in to:
            return None
        elif "@" in to:
            msg['To'] = to
        else:
            msg['To'] = "{}@students.lincoln.ac.uk".format(to)
        msg['Subject'] = subject
        message = MIMEText(html, 'html')
        msg.attach(message)
        return msg

    def huntSendTargets(self, targets):
        """The hunts send targets code"""
        i = 0
        for pair in targets:
            i += 1
            html = open("{}/hunt.html".format(emailTemplateLocation)).read()  # Get the template then edit it
            html = html.replace("[Greeting]", self.greetingGen()).replace("[AddressName]", pair[0]['name']).replace("[TargetName]", pair[1]['name'])
            msg = self.assembleEmail(html, pair[0]['id'])  # assemble the email
            if msg is None:
                print("Not sending Email to {}|Reason: No valid ID/Email".format(pair[0]['name']))  # y u no send
            else:
                self.sendEmails(msg)  # call the send email code

    def VIPSendTargets(self, team, teamleader):
        """VIP's send targets code, NOT FINISHED"""
        i=0
        teamFormatted = ""
        for name in sorted(team):
            teamFormatted += "{}<br>".format(name[0].upper())
        for name in team:
            i += 1
            if name[0][4] != "N/A":
                html = open("{}/VIP.html".format(emailTemplateLocation)).read()
                html = html.replace("[VIPName]", teamleader[0].upper()).replace("[VIPNickname]", teamleader[1]).replace("[TeamList]", teamFormatted)
                msg = self.assembleEmail(html, name[0][4], subject="PRIORITY ORDERS")
                print("{:02}/{} || Sending email to {}".format(i, len(team), msg['To']))
                self.sendEmails(msg)
            elif name[0][4] == "N/A":
                print("{:02}/{} || Could not send target for {}".format(i, len(team), name[0][0]))

        html = open("{}/VIPLeader".format(emailTemplateLocation)).read()
        html = html.replace("[TeamList]", teamFormatted)
        msg = self.assembleEmail(html, teamleader[0][4], subject="YOU ARE BEING TARGETED")
        print(html)



