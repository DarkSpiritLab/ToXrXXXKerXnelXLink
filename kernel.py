
# coding: utf-8

# In[1]:


import json


# In[17]:


# (id,) my_ip,next_ip,next_port,prev_circ_id,next_circ_id,direction,stream_id,is_origin
class link:
    def __init__(self,prev_circ_id,next_circ_id,my_ip,next_ip,next_port,direction,is_origin=False,stream_id=0):
        self.prev_circ_id=prev_circ_id
        self.next_circ_id=next_circ_id
        # self.id=id
        self.my_ip=my_ip
        self.next_ip=next_ip
        self.next_port=next_port
        self.direction=direction
        self.stream_id=stream_id
        self.is_origin=is_origin

def readFromDB():
    '''
    using my_ip as key
    using prev_circ as second key (accelerate search whether prev_circ is there)
    
    return dict() --{"my_ip":{"prev_circ_id":link}}
    '''
    #as test
    relay=dict()
    origin=dict()
    a=link("12","34",1,"10.0.0.1","10.0.0.3",600,123,True)
    b=link("34","56",2,"10.0.0.3","10.0.0.4",700,123)
    origin[a.my_ip]={a.prev_circ_id:a}
    relay[b.my_ip]={b.prev_circ_id:b}
    
    return origin,relay

origins,relays=dict(),dict() #global var
#     return None
def searchNext(p,relays):
    # p:type link  --the previous one 
    # relay:type dict {"my_ip":{"prev_circ_id":link}} --the relay dict
    # return list()  --the list from p to end looks like [p1,[p2,[p3,None]]]
    if(p.next_ip in relays):
        nls=relays[p.next_ip]
        print(nls)
        if(p.next_circ_id in nls): # prev_relay.next_circ_id equals to the next one's prev_circ_id
            t=searchNext(nls[p.next_circ_id],relays)
            return [p,t]
    return None


def linkAll():
    # return fixlinks:type dict("origin_ip":list [[p1,[p2,None]],[p1,[p3,[p4,None]]]])
    fixlinks=dict()
    origins,relays=readFromDB()
    print(origins,relays)
    for oStr in origins:# though all the origin #this is a p
        o=origins[oStr]
        for prev_circ_id in o: #all the next ip
            p=o[prev_circ_id]# one origin link point
            print(p.next_ip)
            t=searchNext(p,relays)
            if(t!=None):
                if(oStr not in fixlinks):
                    fixlinks[oStr]=list()
                fixlinks[oStr].append(t)
    return fixlinks
#             if(next_ip not in relays): #not such relay
#                 continue
#             else:
#                 p=relay[next_ip]
#                 searchNext(p)
if __name__=="__main__":
    print(linkAll())

