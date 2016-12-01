import http.client

class ComponentReporter:
    """
    Class to report statuses, metrics and incidents to Cachet API
    """

    def __init__(self, config):
        """
        Class constructor
         - `config`: Config object
            - `server`: Server FQDN
            - `isHttps`: Use HTTPS (default false)
            - `baseUrl`: API base URL (default `/api/v1`)
            - `apiToken`: API auth token
        """
        self.config = config

    def openConnection(self):
        """
        Open API connection
        """
        if self.config["isHttps"] == "true":
            self.conn = http.client.HTTPSConnection(self.config["server"])
        else:
            self.conn = http.client.HTTPConnection(self.config["server"])

        self.headers = {
            'x-cachet-token': self.config["apiToken"],
            'content-type': "application/json",
            'cache-control': "no-cache",
            }
    def closeConnection(self):
        """
        Close API connection
        """
        self.conn.close()

    def reportStatus(self, passed, config, extraData):
        """
        Report a component status to API
         - `passed`: Is test passed
         - `config`: Reporter test specific config
            - `apiId`: Componenent Id in API
            - `okStatus`: Status if test passed
            - `errorStatus`: Status if test didn't passed
        """
        self.openConnection()
        if(passed):
            payload = "{'status': " + str(config["okStatus"]) + "}"
        else:
            payload = "{'status': " + str(config["errorStatus"]) + "}"
        self.conn.request(
                        "PUT",
                        self.config["baseUrl"] + "/components/" + config["apiId"],
                        payload,
                        self.headers)
        self.closeConnection()

class MetricReporter:
    def __init__(self, config):
        """
        Class constructor
         - `config`: Config object
            - `server`: Server FQDN
            - `isHttps`: Use HTTPS (default false)
            - `baseUrl`: API base URL (default `/api/v1`)
            - `apiToken`: API auth token
        """
        self.config = config

    def openConnection(self):
        """
        Open API connection
        """
        if self.config["isHttps"] == "true":
            self.conn = http.client.HTTPSConnection(self.config["server"])
        else:
            self.conn = http.client.HTTPConnection(self.config["server"])

        self.headers = {
            'x-cachet-token': self.config["apiToken"],
            'content-type': "application/json",
            'cache-control': "no-cache",
            }
    def closeConnection(self):
        """
        Close API connection
        """
        self.conn.close()

    def reportStatus(self, value, config, extraData):
        """
        Report a component status to API
         - `passed`: Is test passed
         - `config`: Reporter test specific config
            - `apiId`: Metric Id in API
        """
        self.openConnection()
        payload = "{'value': " + str(value) + "}"
        self.conn.request(
                        "POST",
                        self.config["baseUrl"] + "/metrics/" + config["apiId"] + "/points",
                        payload,
                        self.headers)
        self.closeConnection()
