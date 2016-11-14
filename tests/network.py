import subprocess, requests, time, socket, re, logging

class PingTest:
    """
    Ping test class
    """
    @staticmethod
    def getName():
        return "PING"

    @staticmethod
    def test(container):
        strings = container.config["urls"].split(';')

        for index, string in enumerate(strings):
            try:
                lastNotify = int(string.split('@')[1])
            except IndexError:
                lastNotify = 0
            url = PingTest.checkUrl(string.split('@')[0])

            if url:
                container.loggerInterface.runningTest("PING")
                process = subprocess.Popen(
                "ping -c 4 -W 1 %s | tail -1 | awk '{print $4}' | cut -d '/' -f 2" % url,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                shell = True
                )

                outs, err = process.communicate()

                if(err):
                    container.loggerInterface.testResult("PING", False, err)
                else:
                    try:
                        ping = float(outs)
                    except ValueError as error:
                        container.loggerInterface.testResult("PING", False, "%s %s \t(%s)" % (error, outs, url))
                    else:
                        if ping > float(container.config["maxPing"]):
                            container.loggerInterface.testResult("PING", False, "%s > %s\t(%s)" % (str(ping), self.config["maxPing"], url))
                        else:
                            container.loggerInterface.testResult("PING", True, "%s OK\t(%s)" % (str(ping), url))
            else:
                container.loggerInterface.testResult("PING", False, "Not valid URL")

        container.finish()

    @staticmethod
    def checkUrl(url):
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

    @staticmethod
    def getName():
        return "HTTP"

    @staticmethod
    def test(container):
        strings = container.config["urls"].split(';')

        for index, string in enumerate(strings):
            try:
                lastNotify = int(string.split('@')[1])
            except IndexError:
                lastNotify = 0
            url = string.split('@')[0]

            container.loggerInterface.runningTest("HTTP")

            status, reason, realUrl = HTTPErrorTest.makeRequest(url)

            if status >= 400 and status < 600 or status == 302:
                # An error occured (4xx or 5xx codes) or temporary redirect was found(302)
                if(lastNotify + int(container.config["notificationInterval"]) < int(time.time())):
                    container.loggerInterface.testResult("HTTP", False, "%s: %s \t(%s)" % (status, reason, realUrl))
                    extraData = {"siteName": url, "message": "%s: %s" % (status, reason)}
                    container.report(False, extraData)
                    newString = realUrl + "@" + str(int(time.time()))
                    strings[index] = newString
                else:
                    container.loggerInterface.testResult("HTTP", False, "%s: %s \t(%s) Not notified" % (status, reason, realUrl))
            else:
                container.loggerInterface.testResult("HTTP", True, "%s: %s \t(%s)" % (status, reason, realUrl))
                newString = realUrl
                strings[index] = newString

        newConfig = ""
        for index, string in enumerate(strings):
            if(index != 0):
                newConfig += ";"
            newConfig += string
        container.config["urls"] = newConfig

        container.finish()

    @staticmethod
    def makeRequest(url):
        validUrl, protocol =  HTTPErrorTest.checkUrl(url)
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
                message = error.args
                status = 410
                reason = message
                cleanUrl = url
        else:
            status = 501
            reason = "Invalid URL"
            cleanUrl = url

        return status, reason, cleanUrl

    def checkUrl(url):
        regex = r"(https?://)?([a-z-\.0-9]*/?[a-z-\.0-9]*[\.[a-z]+/?)(:[0-9]+)?"
        m = re.match(regex, url)

        protocol = m.group(1)

        if m:
            return True, protocol
        else:
            return False, protocol
