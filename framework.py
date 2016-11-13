import logging, sys, os, time, atexit, signal, queue, autoload

class Core:
    @staticmethod
    def executeRunner(config, reporters):
        runner = Runner(config, reporters)
        runner.load()
        runner.run()

    @staticmethod
    def getTestsInstance(name):
        return autoload.getTests()[name]

class Runner:
    """

    """

    def __init__(self, config, reporters):
        self.statuses = {
         0: 'IDLE',
         1: 'INITIALIZING',
        10: 'INITIALIZING_OK',
        11: 'INITIALIZING_ERR',
         2: 'SWITCHING',
        20: 'SWITCHING_OK',
        21: 'SWITCHING_ERR',
         3: 'TESTING',
        30: 'TESTING_OK',
        31: 'TESTING_ERR'
        }
        self.config = config
        self.logger = config["logger"]
        self.tag = "runner %s" % config["name"]
        self.reporters = reporters

        self.setStatus(0)

    def load(self):
        self.logger.info(self.tag, "Initializing")
        self.setStatus(1)

        tests = self.config.sections
        testsNb = len(tests)
        self.logger.debug(self.tag, "%d tests found" % testsNb)

        self.testQueue = queue.Queue(testsNb)
        for test in tests:
            self.logger.debug(self.tag, "Enqueuing %s" % test)
            try:
                self.testQueue.put(Core.getTestsInstance(test), True, 1)
            except:
                self.logger.critical(self.tag, "Enqueuing %s failed. Stopping initialization" % test)
                self.setStatus(11)
                raise
        self.logger.info(self.tag, "Initialized successfully")
        self.setStatus(10)

    def run(self):
        self.logger.info(self.tag, "Starting %d tests" % self.testQueue.qsize())
        #TODO Parse conf to inject global in specific
        self._next()
        self.setStatus(30)

    def _next(self):
        self.setStatus(2)
        if not self.testQueue.empty():
            test = self.testQueue.get(True, 1)
            container = TestContainer(test, self.config[test.getName()], self.logger, self.reporters)
            self.setStatus(3)
            container.start()
            self._next()

    #######
    #UTILS#
    #######
    def setStatus(self, status):
        self.logger.debug(self.tag, "Switchig to status %d: %s" % (status, self.statuses[status]))
        self.status =  status

class TestContainer:
    def __init__(self, test, config, loggerInterface, reporters):
        self.test = test
        self.config = config
        self.loggerInterface = loggerInterface
        self.reporters = reporters

    def start(self):
        self.running = True
        self.test.test(self)

        while self.running:
            pass
    def finish(self):
        self.running = False

    def report(self, result, extraData = {}):
        try:
            reportersToCall = self.config["REPORTERS"].sections
        except KeyError:
            #No reporters
            pass
        else:
            for reporter in reportersToCall:
                self.reporters[reporter].reportStatus(result, self.config["REPORTERS"][reporter], extraData)

class Logger:
    """
    Logger class
    """
    def __init__(self, config):
        """
        Class constructor
         - `config`: Logger configuration
            - `consoleLevel`: Log level for console logging (default info)
        """
        self.logger = logging.getLogger("matahari")
        self.logger.setLevel(logging.DEBUG)

        self.consoleHandler = logging.StreamHandler()
        self.consoleHandler.setLevel(self.mapLogLevel(config["consoleLevel"]))

        self.logger.addHandler(self.consoleHandler)

    def critical(self, tag, message):
        self.logger.critical("\033[1;5;41m[%s]: \t %s\033[0m" % (tag, message))

    def error(self, tag, message):
        self.logger.error("\033[31m[%s]: \t %s\033[0m" % (tag, message))

    def warning(self, tag, message):
        self.logger.warning("\033[33m[%s]: \t %s\033[0m" % (tag, message))

    def info(self, tag, message):
        self.logger.info("\033[34m[%s]: \t %s\033[0m" % (tag, message))

    def debug(self, tag, message):
        self.logger.debug("[%s]: \t %s" % (tag, message))

    def logInterrupt(self, tag, message):
        self.logger.info("\b\b\033[34m[%s]: \t %s\033[0m" % (tag, message))

    def header(self, message):
        self.logger.info("\033[1m%s\033[0m\n" % message)

    def testResult(self, test, isPassed, details = ""):
        if isPassed == True:
            message = "   \033[32m[PASSED] %s\033[0m\t%s\n"
        else:
            message = "   \033[31m[FAILED] %s\033[0m\t%s\n"
        self.logger.info(message % (test, details))

    def runningTest(self, test):
        message = "   \033[33m[ WAIT ] %s \033[0m\033[F"
        self.logger.info(message % test)

    def mapLogLevel(self, level):
        logLevels = {}

        logLevels["debug"] = logging.DEBUG
        logLevels["info"] = logging.INFO

        return logLevels[level] or logging.DEBUG

class Daemon:
    """A generic daemon class.

    Usage: subclass the daemon class and override the run() method."""

    def __init__(self, pidfile, runtime):
        self.pidfile = pidfile
        self.runtime = runtime

    def daemonize(self):
    	"""Deamonize class. UNIX double fork mechanism."""

    	try:
    		pid = os.fork()
    		if pid > 0:
    			# exit first parent
    			sys.exit(0)
    	except OSError as err:
    		sys.stderr.write('fork #1 failed: {0}\n'.format(err))
    		sys.exit(1)

    	# decouple from parent environment
    	os.chdir('/')
    	os.setsid()
    	os.umask(0)

    	# do second fork
    	try:
    		pid = os.fork()
    		if pid > 0:

    			# exit from second parent
    			sys.exit(0)
    	except OSError as err:
    		sys.stderr.write('fork #2 failed: {0}\n'.format(err))
    		sys.exit(1)

    	# redirect standard file descriptors
    	sys.stdout.flush()
    	sys.stderr.flush()
    	si = open(os.devnull, 'r')
    	so = open('/var/log/matahari.log', 'a+')
    	se = open('/var/log/matahari.log', 'a+')

    	os.dup2(si.fileno(), sys.stdin.fileno())
    	os.dup2(so.fileno(), sys.stdout.fileno())
    	os.dup2(se.fileno(), sys.stderr.fileno())

    	# write pidfile
    	atexit.register(self.delpid)

    	pid = str(os.getpid())
    	with open(self.pidfile,'w+') as f:
    		f.write(pid + '\n')

    def delpid(self):
    	os.remove(self.pidfile)

    def start(self):
    	"""Start the daemon."""

    	# Check for a pidfile to see if the daemon already runs
    	try:
    		with open(self.pidfile,'r') as pf:

    			pid = int(pf.read().strip())
    	except IOError:
    		pid = None

    	if pid:
    		message = "pidfile {0} already exist. " + \
    				"Daemon already running?\n"
    		sys.stderr.write(message.format(self.pidfile))
    		sys.exit(1)

    	# Start the daemon
    	self.daemonize()
    	self.run()

    def stop(self):
    	"""Stop the daemon."""

    	# Get the pid from the pidfile
    	try:
    		with open(self.pidfile,'r') as pf:
    			pid = int(pf.read().strip())
    	except IOError:
    		pid = None

    	if not pid:
    		message = "pidfile {0} does not exist. " + \
    				"Daemon not running?\n"
    		sys.stderr.write(message.format(self.pidfile))
    		return # not an error in a restart

    	# Try killing the daemon process
    	try:
    		while 1:
    			os.kill(pid, signal.SIGTERM)
    			time.sleep(0.1)
    	except OSError as err:
    		e = str(err.args)
    		if e.find("No such process") > 0:
    			if os.path.exists(self.pidfile):
    				os.remove(self.pidfile)
    		else:
    			print (str(err.args))
    			sys.exit(1)

    def restart(self):
    	"""Restart the daemon."""
    	self.stop()
    	self.start()

    def run(self):
        """You should override this method when you subclass Daemon.

        It will be called after the process has been daemonized by
        start() or restart()."""
        self.runtime()

# Utils functions
def initReporters(reporters, config):
    """
    Init all reporters in `reporters` if a config section found in `config`
    """
    configuredReporters = config.sections
    for reporter in reporters:
        if(reporter in configuredReporters):
            reporters[reporter] = reporters[reporter](config[reporter])
        else:
            del reporters[reporter]
    return reporters
