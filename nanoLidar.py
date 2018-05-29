# nanoLidar.py 
# Class for the self made nanoLidar
#

import pika
import uuid
import math

#------------------------------------
# setup message queueing
#------------------------------------
class lidarRpcClient(object):
    def __init__(self, hostname,user,passwd):
        self.cred = pika.PlainCredentials(user, passwd)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=hostname,credentials=self.cred))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='lidar_queue',
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=n.encode('utf-8'))
        while self.response is None:
            self.connection.process_data_events()
        return self.response

#------------------------------------
# LIDAR class
#------------------------------------
class nanoLidar:
    'Class for the self made nanoLidar'
    
    def __init__(self):
        # 360 elements (distance in mm), indexed by angle
        self.map = []
        # scan number
        self.scan_num = -1
        # sensor offset from center [mm]
        self.offset = 17
        # initialize message queueing
        self.lidarRpc = lidarRpcClient('localhost','x200','bone')

    def getInfo(self):
        # read firmware information
        return self.lidarRpc.call('info#').decode('utf-8')

    def scan(self, xp, yp, theta):
        # robot position xp, yp in [mm]
        # robot direction theta in degrees
        self.scan_num = self.scan_num + 1

        # start 360 degree scan
        lines = self.lidarRpc.call('scan#').decode('utf-8').split('\r\n')
        # read scan data
        for line in lines:
            if line != '':
                (angle, dist_cm, strength) = line.split(',')
                rad = math.radians(int(angle) + theta)
                dist = int(dist_cm)*10 + self.offset
                # maximum reliable distance: 6000 mm
                if dist <= 6000:
                    x = xp + (dist * math.cos(rad))
                    y = yp + (dist * math.sin(rad))
                    self.map.append((self.scan_num,x,y))        

        # done
        return True

    def getNumPoints(self):
        return len(self.map)

    def getNumScans(self):
        return self.scan_num
		        
