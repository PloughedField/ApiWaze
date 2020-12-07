from api_waze import WazeRouteCalculator
import datetime
import time
import json
import pika


from_address = 'Oranit'
to_address = 'Tel Aviv'
region = 'IL'
ELASTIC_DATETIME = "%Y-%m-%dT%H:%M%S.%f"
TIME = int(time.time())

class Traffic :

    def __init__(self):
        self.connection = pika.BlockingConnection()
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='api',exchange_type ='direct',passive=False,durable=True,auto_delete=False)
        self.channel.queue_declare(queue='waze',durable=True)
        self.channel.queue_bind(exchange='api',queue='waze',routing_key='logstash')

        self.route = WazeRouteCalculator(from_address, to_address, region)
        self.route_time, self.route_distance = self.route.calc_route_info()
        self.route1 = WazeRouteCalculator(to_address, from_address, region)
        self.route_time1, self.route_distance1= self.route1.calc_route_info()

        print('Time %.2f minutes, distance %.2f km.' % (self.route_time, self.route_distance))

        print('Time1 %.2f minutes, distance %.2f km.' % (self.route_time1, self.route_distance1))

    def chack_traffic_go(self):

        if  self.route_time > 40 :
            traffic_congestion = "High"
        elif  30 < self.route_time < 40 :
            traffic_congestion = "Medium"
        elif  self.route_time < 30 :
            traffic_congestion = "Low"

        GO = {"distance": self.route_distance,
               "time": self.route_time,
               "from_address": from_address,
               "to_address": to_address,
               "date": datetime.datetime.fromtimestamp(TIME).strftime(ELASTIC_DATETIME),
               "traffic_congestion":traffic_congestion}
        return GO

    def chack_traffic_back(self):

        if  self.route_time1 > 40 :
            traffic_congestion1 = "High"
        elif  30 < self.route_time1 < 40 :
            traffic_congestion1 = "Medium"
        elif  self.route_time1 < 30 :
            traffic_congestion1 = "Low"

        BACK = {"distance": self.route_distance1,
                "time": self.route_time1,
                "from_address": to_address,
                "to_address": from_address,
                "date": datetime.datetime.fromtimestamp(TIME).strftime(ELASTIC_DATETIME),
                "traffic_congestion": traffic_congestion1}
        print(BACK)
        return BACK

    def send_rabbit(self):

        self.channel.basic_publish(exchange='api', routing_key='logstash',
                              body=json.dumps(self.chack_traffic_go()))
        print("send go to rabbit")
        self.channel.basic_publish(exchange='api', routing_key='logstash',
                              body=json.dumps(self.chack_traffic_back()))
        print("send back to rabbit")
        self.connection.close()







while True :
    try:
        print('Please wait to connect')
        time.sleep(60)

        route = Traffic()
        route.chack_traffic_go()
        route.chack_traffic_back()

        route.send_rabbit()
        time.sleep(900)
    except Exception as error:
        print(error)








