import smtplib
from email.mime.text import MIMEText

class MailReporter:
    """
    Send report by mail
    """
    def __init__(self, config):
        """
        Class constructor
         - `config`: Config object
        """
        self.config = config

    def reportStatus(self, passed, config, extraData):
        """
        Report a component status to API
         - `passed`: Is test passed
         - `config`: Reporter test specific config
        """
        if passed == False:
            message = """PING DOWN Report\nLe site %s à retourné une erreur lors du dernier test (%s),\ntu devrais y jetter un oeil rapidement ;)\nMatahari
            """ % (extraData['siteName'], extraData['message'])

            msg = MIMEText(message)
            msg['Subject'] = '%s DOWN' % extraData['siteName']
            msg['From'] = self.config['fromAddress']
            msg['To'] = self.config['toAddress']

            s = smtplib.SMTP('localhost')
            s.send_message(msg)
            s.quit()
