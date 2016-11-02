import subprocess, requests, time, socket, re, logging

class PingTest:
    """
    Ping test class
    """

    def __init__(self, config, reporters, logger):
        """
        Test constructor
         - `config`: config object used in test
         - `reporters`: List of Reporter instances used to report test result
         - `logger`: Logger instance used to log operations
        """
        self.config = config
        self.reporters = reporters
        self.logger  = logger

    def test(self):
        strings = self.config["urls"].split(';')

        for index, string in enumerate(strings):
            try:
                lastNotify = int(string.split('@')[1])
            except IndexError:
                lastNotify = 0
            url = self.checkUrl(string.split('@')[0])

            if url:
                self.logger.runningTest("PING")
                process = subprocess.Popen(
                "ping -c 4 -W 1 %s | tail -1 | awk '{print $4}' | cut -d '/' -f 2" % url,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                shell = True
                )

                outs, err = process.communicate()

                if(err):
                    self.logger.testResult("PING", False, err)
                else:
                    try:
                        ping = float(outs)
                    except ValueError as error:
                        self.logger.testResult("PING", False, "%s %s \t(%s)" % (error, outs, url))
                    else:
                        if ping > float(self.config["maxPing"]):
                            self.logger.testResult("PING", False, "%s > %s\t(%s)" % (str(ping), self.config["maxPing"], url))
                        else:
                            self.logger.testResult("PING", True, "%s OK\t(%s)" % (str(ping), url))
            else:
                self.logger.testResult("PING", False, "Not valid URL")

    def checkUrl(self, url):
        regex = r"(https?://)?([a-z-\.0-9]*/?[a-z-\.0-9]*\.[a-z]+)/?(:[0-9]+)?"
        m = re.match(regex, url)

        if m:
            return m.group(2)
        else:
            return False

class HTTPErrorTest:
    """
    Test HTTP request code. Report for 4xx and 5xx
    """

    def __init__(self, config, reporters, logger):
        """
        Test constructor
         - `config`: config object used in test
         - `reporters`: List of Reporter instances used to report test result
         - `logger`: Logger instance used to log operations
        """
        self.config = config
        self.reporters = reporters
        self.logger  = logger

        logging.getLogger('urllib3').setLevel(logging.WARNING)


    def test(self):
        strings = self.config["urls"].split(';')

        for index, string in enumerate(strings):
            try:
                lastNotify = int(string.split('@')[1])
            except IndexError:
                lastNotify = 0
            url = string.split('@')[0]

            self.logger.runningTest("HTTP")

            status, reason, realUrl = self.makeRequest(url)

            if status >= 400 and status < 600 or status == 302:
                # An error occured (4xx or 5xx codes) or temporary redirect was found(302)
                if(lastNotify + int(self.config["notificationInterval"]) < int(time.time())):
                    self.logger.testResult("HTTP", False, "%s: %s \t(%s)" % (status, reason, realUrl))
                    self.report(False, url, "%s: %s" % (status, reason))
                    newString = realUrl + "@" + str(int(time.time()))
                    strings[index] = newString
                else:
                    self.logger.testResult("HTTP", False, "%s: %s \t(%s) Not notified" % (status, reason, realUrl))
            else:
                self.logger.testResult("HTTP", True, "%s: %s \t(%s)" % (status, reason, realUrl))
                newString = realUrl
                strings[index] = newString

        newConfig = ""
        for index, string in enumerate(strings):
            if(index != 0):
                newConfig += ";"
            newConfig += string
        self.config["urls"] = newConfig

        return self.config


    def report(self, result, siteName, message):
        reportersToCall = self.config["REPORTERS"].sections

        for reporter in reportersToCall:
            self.config["REPORTERS"][reporter]["siteName"] = siteName
            self.config["REPORTERS"][reporter]["message"] = message
            config = self.config["REPORTERS"][reporter]
            self.reporters[reporter].reportStatus(result, config)

    def makeRequest(self, url):
        validUrl, protocol =  self.checkUrl(url)
        if validUrl:
            try:
                if(protocol == None):
                    response = requests.get("http://" + url)
                else:
                    response = requests.get(url)
                status = response.status_code
                reason = response.reason
                cleanUrl = response.url
            except requests.exceptions.ConnectionError as error:
                code, message = error.args
                status = 410
                reason = message
                cleanUrl = url
        else:
            status = 501
            reason = "Invalid URL"
            cleanUrl = url

        return status, reason, cleanUrl

    def checkUrl(self, url):
        regex = r"(https?://)?([a-z-\.0-9]*/?[a-z-\.0-9]*[\.[a-z]+/?)(:[0-9]+)?"
        m = re.match(regex, url)

        protocol = m.group(1)

        if m:
            return True, protocol
        else:
            return False, protocol
