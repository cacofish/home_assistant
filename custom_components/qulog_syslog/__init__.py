"The Syslogger for Qulog Integration."

import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from . import sysloggercommon
from . import syslogger_tcp
from . import syslogger_udp

DOMAIN = "qulog_syslog"

CONF_SERVER = "server"
CONF_PORT = "port"
CONF_PROTOCOL = "protocol"

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_SERVER): cv.string,
        vol.Required(CONF_PORT): cv.positive_int,
        vol.Required(CONF_PROTOCOL): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)

ATTR_FACILITY = "facility"
ATTR_APPLICATION = "application"
DEFAULT_APPLICATION = "ha_script"
ATTR_PROCESS = "process"
DEFAULT_PROCESS = "-"

ATTR_MESSAGE = "message"
DEFAULT_MESSAGE = "Default Log Message"

ATTR_LOGLEVEL = "loglevel"
DEFAULT_LOGLEVEL = "info"

def setup(hass, config):
    def handle_logmessage(call):
        sysserver = config[DOMAIN][CONF_SERVER]
        port = config[DOMAIN][CONF_PORT]
        protocol = config[DOMAIN][CONF_PROTOCOL]
        sysloggercommon.LOGGER.debug("Server: {}://{}:{}".format(protocol, sysserver, port))
        facility = call.data.get(ATTR_FACILITY, "USER")
        application = call.data.get(ATTR_APPLICATION, DEFAULT_APPLICATION)
        process = call.data.get(ATTR_PROCESS, DEFAULT_PROCESS)

        messagetext = call.data.get(ATTR_MESSAGE, DEFAULT_MESSAGE)
        loglevel = call.data.get(ATTR_LOGLEVEL, DEFAULT_LOGLEVEL)     
        
        try:
          if ("TCP" == protocol):
            log = syslogger_tcp.Syslog(sysserver, port, sysloggercommon.sysfacility(facility))
            log.send(application, process, messagetext, sysloggercommon.sysloglevel(loglevel))
          else:
            log = syslogger_udp.Syslog(sysserver, port, sysloggercommon.sysfacility(facility))
            log.send(application, process, messagetext, sysloggercommon.sysloglevel(loglevel))
        except Exception as e:
          sysloggercommon.LOGGER.error("Problem sending to Remote Syslog server, ", str(e))

    hass.services.register(DOMAIN, 'logmessage', handle_logmessage)
    sysloggercommon.LOGGER.info("Registered handle_logmessage")

    # Return boolean to indicate that initialization was successful.
    return True