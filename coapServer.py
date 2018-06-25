#!/usr/bin/python3

import serial
import datetime
import logging

import asyncio

import aiocoap.resource as resource
import aiocoap

#------------------------------------
# setup serial connections
#------------------------------------
robot = serial.Serial('/dev/ttyS4')
lidar = serial.Serial('/dev/ttyS5',57600)

class commandRobotResource(resource.Resource):
    """Resource which supports the PUT method. It sends a command
    to the robot module"""

    def get_link_description(self):
        # Publish additional data in .well-known/core
        return dict(**super().get_link_description(), title="Send command to robot module")

    def command(cmd):
        rc = ""
        result = ""
        robot.write(cmd.encode('utf-8'))
        robot.flush()
        while rc != 'ok':
            rc = robot.readline().decode('utf-8').rstrip('\r\n')
            result = result + rc + '\n'
        return result

    async def render_put(self, request):
        response = self.command(body.decode('utf-8'))
        print('PUT payload: %s' % request.payload)
        self.set_content(request.payload)
        return aiocoap.Message(code=aiocoap.CHANGED, payload=self.content)


class scanLidarResource(resource.Resource):
    """Resource which supports the GET method. It starts a 360° scan
    of the LIDAR module"""

    def get_link_description(self):
        # Publish additional data in .well-known/core
        return dict(**super().get_link_description(), title="Get Lidar 360° scan")

    async def render_get(self, request):
        lidar.write('scan#'.encode('utf-8'))
        lidar.flush()
        response = ''
        for i in range(360):
            line = lidar.readline().decode('utf-8')
            response = response + line
        return aiocoap.Message(payload=response)


class infoLidarResource(resource.Resource):
    """Resource which supports the GET method. It reads the firmware version
    of the LIDAR module"""

    def get_link_description(self):
        # Publish additional data in .well-known/core
        return dict(**super().get_link_description(), title="Get Lidar firmware version")

    async def render_get(self, request):
        lidar.write('info#'.encode('utf-8'))
        lidar.flush()
        response = ''
        response = lidar.readline().decode('utf-8')
        response = response + lidar.readline().decode('utf-8')
        return aiocoap.Message(payload=response)

# logging setup
logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)

def main():
    # Resource tree creation
    root = resource.Site()

    root.add_resource(('.well-known', 'core'),
            resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(('robot', 'command'), commandRobotResource())
    root.add_resource(('lidar', 'scan'), scanLidarResource())
    root.add_resource(('lidar', 'info'), infoLidarResource())

    asyncio.Task(aiocoap.Context.create_server_context(root))

    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
