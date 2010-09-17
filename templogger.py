#!/usr/bin/env python

import socket
import sys
import smtplib

from email.mime.text import MIMEText
from time import sleep

class TempReader:

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

    def __readsocket(self, command='*SRTC'):
        command = command + '\n'
        print 'Connecting to %s %d' % (self.hostname, self.port)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.hostname, self.port))
        s.send(command)
        data = s.recv(1024)
        s.close
        sleep(0.5)
        return data

    def temperature(self):
        return float(self.__readsocket('*SRTC'))

    def humidity(self):
        return float(self.__readsocket('*SRH'))

    def dewpoint(self):
        return float(self.__readsocket('*SRD'))

class EnvironmentChecker:

    def __init__(self, hostname, port, templow, temphigh, humiditylow, humidityhigh, to, f, logfile):
        self.hostname = hostname
        self.t = TempReader(hostname, port)
        self.templow = templow
        self.temphigh = temphigh
        self.humiditylow = humiditylow
        self.humidityhigh = humidityhigh
        self.to = to
        self.f = f
        self.logfile = logfile

        self.temp = 0.0
        self.hum = 0.0
        self.dew = 0.0

    def check(self):
        try:
            self.temp = self.t.temperature()
            self.hum = self.t.humidity()
            self.dew = self.t.dewpoint()

            if outofspec(self.temp, self.templow, self.temphigh):
                self.notify("Temperature out of valid range")
            elif outofspec(self.hum, self.humiditylow, self.humidityhigh):
                self.notify("Humidity out of valid range")
            elif self.temp <= self.dew:
                self.notify("Temperature below dewpoint")
            else:
                print "ok"
        except socket.error, msg:
            self.notify("Unable to check environment", str(msg))

    def notify(self, subject, msg=None):
        if msg == None:
            msg = """
Current values are:
\tTemperature: %.1f \t(low: %.1f, high: %.1f)
\tHumidity: %.1f \t(low: %.1f, high: %.1f)
\tDewpoint: %.1f""" % (self.temp, self.templow, self.temphigh, self.hum, self.humiditylow, self.humidityhigh, self.dew)

        subject = '%s for %s' % (subject, self.hostname)
        sendmail(self.to, self.f, subject, msg)



def outofspec(current, low, high):
    return current < low or current > high

def sendmail(to, f, subject, data):
    msg = MIMEText(data)
    msg['From'] = f
    msg['To'] = to
    msg['Subject'] = subject
    s = smtplib.SMTP('mail.sensors.elex.be')
    s.sendmail(f, [to], msg.as_string())
    s.quit()


if __name__ == '__main__':
    (prog, host, tl, th, hl, hh, email, smtp, log, port) = sys.argv[:10]
    e = EnvironmentChecker(host, int(port), float(tl), float(th), float(hl), float(hh), email, "brh@melexis.com", log)
    e.check()

