# based on https://csl.name/post/python-syslog-client/
# delivers messages in BSD (legacy Syslog) format
import socket
from datetime import datetime 
import uuid

from . import sysloggercommon

class Syslog:

  def __init__(self,
               sysserver="localhost",
               port=1514,
               facility=sysloggercommon.Facility.DAEMON):
    self.sysserver = sysserver
    self.port = port
    self.facility = facility
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  def get_mac(self):
    mac_num = hex(uuid.getnode()).replace('0x', '').upper()
    mac = ':'.join(mac_num[i: i + 2] for i in range(0, 11, 2))
    return mac

  def get_ip_address(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((self.sysserver, self.port))
    return s.getsockname()[0]

  def send(self, application, process, messageid, message, level):
    data = ('<{priority}>1 {time} {hostname} {application} {process} {messageid} '
            '[QULOG@EVENT MAC="{mac}" IP="{ip}" USER="homeassistant" SOURCE="{hostname}" '
            'COMPUTER="" APPLICATION="{process}" APPLICATION_ID="" CATEGORY="{messageid}" CATEGORY_ID="" '
            'MESSAGE_ID="" EXTRA_DATA="" CLIENT_ID="" CLIENT_APP="{application}" CLIENT_AGENT=""]'
            ' {logmessage}').format(
        priority=(level + self.facility*8), 
        time=datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
        hostname=socket.gethostname(), 
        application=application, 
        process=process,
        messageid=messageid,
        mac=self.get_mac(),
        ip=self.get_ip_address(),
        logmessage=message)
    sysloggercommon.LOGGER.debug("Sending UDP://{}:{} with data: {}".format(self.sysserver, self.port, data))
    self.socket.sendto(data.encode(), (self.sysserver, self.port))