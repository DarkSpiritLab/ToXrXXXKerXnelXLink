from collections import defaultdict
import mysql.connector
import datetime

import json


query = ("select my_ip,next_ip,next_port,prev_circ_id,next_circ_id,direction,stream_id,is_origin from net "
         "where time between %s and %s ")


config={}
with open("config") as f:
    t=f.readlines()
    config=json.loads(t)


# id,my_ip,next_ip,next_port,prev_circ_id,next_circ_id,direction,stream_id,is_origin
class link:
    def __init__(self, my_ip, next_ip, next_port, prev_circ_id, next_circ_id, direction, stream_id = 0,
                 is_origin = False, id = 0):
        self.prev_circ_id = prev_circ_id
        self.next_circ_id = next_circ_id
        self.id = id
        self.my_ip = my_ip
        self.next_ip = next_ip
        self.next_port = next_port
        self.direction = direction
        self.stream_id = stream_id
        self.is_origin = is_origin

    def __str__(self):
        return str("my_ip:" + self.my_ip)


def readFromDB(offset = 30):
    '''
    using my_ip as key
    using prev_circ as second key (accelerate search whether prev_circ is there)

    type offset:int  (minute)
    rtype dict() --{"my_ip":{"prev_circ_id":link}}
    '''
    relay = defaultdict(dict)
    origin = defaultdict(dict)

    time_start="(select date_sub( ( select now() ), interval %d minute ))"%offset
    time_end="( select now() )"

    cnx = mysql.connector.connect(**config)
    cursor=cnx.cursor()

    cursor.execute(query,(time_start,time_end))

    for (my_ip,next_ip,next_port,prev_circ_id,next_circ_id,direction,stream_id,is_origin) in cursor:
        t=link(my_ip,next_ip,next_port,prev_circ_id,next_circ_id,direction,stream_id,is_origin)
        if(is_origin):
            origin[t.my_ip][t.prev_circ_id]=t
        else:
            relay[t.my_ip][t.prev_circ_id]=t
    # as test

#     a = link("10.0.0.1", "10.0.0.3", 600, "12", "34", 1, 123, True)
#     b = link("10.0.0.3", "10.0.0.4", 700, "34", "56", 2, 123)
#     c = link("10.0.0.4", "10.0.0.7", 999, "56", "11111", 3, 123)
#     origin[a.my_ip] = {a.prev_circ_id: a}
#     relay[b.my_ip] = {b.prev_circ_id: b}
#     relay[c.my_ip] = {c.prev_circ_id: c}
    cnx.close()
    return origin, relay


origins, relays = defaultdict(dict), defaultdict(dict)  # global var


#     return None
def searchNext(p, relays):
    # todo using direction to estimate whether this relay is right
    # p:type link  --the previous one
    # relay:type dict {"my_ip":{"prev_circ_id":link}} --the relay dict
    # return list()  --the list from p to end looks like [p1,p2,p3]
    if (p.next_ip in relays):
        nls = relays[p.next_ip]
        #         print(nls)
        if (p.next_circ_id in nls):  # prev_relay.next_circ_id equals to the next one's prev_circ_id
            t = searchNext(nls[p.next_circ_id], relays)
            if (t is not None):
                t.insert(0, p)
                return t
            else:
                # as end one is nls[p.next_circ_id]
                return [p,nls[p.next_circ_id]]
    return None


def printFixLinks(fixlinks):
    # type fixlinks:dict("origin_ip":list [[p1,p2,p3],[p1,p3,p4,p5]])
    #     print(fixlinks)
    for i in fixlinks:
        for ii in fixlinks[i]:
            for node in ii:
                print(node.my_ip + "->")
            print("end one:"+ii[-1].next_ip)


def linkAll():
    # rtype fixlinks: dict("origin_ip":list [[p1,p2,p3],[p1,p3,p4,p5]])
    fixlinks = defaultdict(list)
    origins, relays = readFromDB()
    #     print(origins,relays)
    for oStr in origins:  # though all the origin #this is a p
        o = origins[oStr]
        for prev_circ_id in o:  # all the next ip
            p = o[prev_circ_id]  # one origin link point

            t = searchNext(p, relays)
            if (t != None):
                fixlinks[oStr].append(t)
    return fixlinks


if __name__ == "__main__":
    a = linkAll()
    printFixLinks(a)
