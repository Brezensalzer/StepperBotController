#!/usr/bin/python3
import pika
import serial

#------------------------------------
# setup message queueing
#------------------------------------
cred = pika.PlainCredentials('beagle', 'bone')
mq_conn = pika.BlockingConnection(pika.ConnectionParameters(
        host='192.168.10.103',credentials=cred))
mq_channel = mq_conn.channel()
mq_channel.queue_declare(queue='stepper_queue')
mq_channel.queue_declare(queue='lidar_queue')

#------------------------------------
# setup serial connections
#------------------------------------
robot = serial.Serial('/dev/ttyS4')
lidar = serial.Serial('/dev/ttyS5',57600)

def command(cmd):
    rc = ""
    result = ""
    robot.write(cmd.encode('utf-8'))
    robot.flush()
    while rc != 'ok':
        rc = robot.readline().decode('utf-8').rstrip('\r\n')
        result = result + rc + '\n'
    return result


def on_request_stepper(ch, method, props, body):
    response = command(body.decode('utf-8'))

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = props.correlation_id),
                     body=response.encode('utf-8'))
    ch.basic_ack(delivery_tag = method.delivery_tag)

def on_request_lidar(ch, method, props, body):
    response = body.decode('utf-8')
    if response == 'info#':
        lidar.write('info#'.encode('utf-8'))
        lidar.flush()
        response = ''
        response = lidar.readline().decode('utf-8')
        response = response + lidar.readline().decode('utf-8')

    if response == 'scan#':
        lidar.write('scan#'.encode('utf-8'))
        lidar.flush()
        response = ''
        for i in range(360):
            line = lidar.readline().decode('utf-8')
            response = response + line
            
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = props.correlation_id),
                     body=response.encode('utf-8'))
    ch.basic_ack(delivery_tag = method.delivery_tag)

mq_channel.basic_qos(prefetch_count=1)
mq_channel.basic_consume(on_request_stepper, queue='stepper_queue')
mq_channel.basic_consume(on_request_lidar, queue='lidar_queue')

print(" [x] Awaiting RPC requests")
mq_channel.start_consuming()

