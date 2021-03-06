#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2020, Bosch Rexroth AG
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os 
import sys
import signal
import time
import sqlite3
from sqlite3 import Error
import json

import ctrlxdatalayer
from ctrlxdatalayer.variant import Variant

import app.nodes
import app.utils

def main():

    with ctrlxdatalayer.system.System("") as datalayer_system:
        datalayer_system.start(False)

        provider = datalayer_system.factory().create_provider("ipc://")
        if provider is None:
            sys.exit(1)

        with provider:  # provider.close() is called automatically when leaving with block

            offset = [0, 0]                                 # fetch offsets [queue, history]
            auto = True 
    
            db = "file:memdb1?mode=memory&cache=shared"     # in-memory database      
    
            base = app.utils.initialize(db)                 # leave one connection instance open to maintain memory
            base.execute("pragma journal_mode=wal;")        # configure database in "write-ahead log" mode


            result = provider.start()
            if result is not ctrlxdatalayer.variant.Result.OK:
                print("ERROR Starting Data Layer Provider failed with:", result)
                return

            node_push = app.nodes.Push(provider, db)        # add job to queue
            node_push.register_node()

            node_pop = app.nodes.Pop(provider, db)          # pop job from queue
            node_pop.register_node()

            node_count = app.nodes.Count(provider, db)      # return queue/pending count, write zero to dump
            node_count.register_node()

            node_done =  app.nodes.Done(provider, db)       # add item to db or mark item in db as done
            node_done.register_node()

            node_history = app.nodes.History(provider, db)  # fetch items from history
            node_history.register_node()

            node_auto = app.nodes.Auto(provider, auto)      # automatically generate job orders when true
            node_auto.register_node()


            while provider.is_connected():

                conn = app.utils.initialize(db)
                if conn: 
                    if app.utils.count_queue(conn) == 0  and node_auto.value():
                        app.utils.add_virtual_job_order(conn, 3)

                        conn.close()


                time.sleep(5.0)                               # sleep in seconds


            node_push.unregister_node()
            del node_push

            node_pop.unregister_node()
            del node_pop

            node_count.unregister_node()
            del node_count        

            node_done.unregister_node()
            del node_done

            node_history.unregister_node()
            del node_history

            node_auto.unregister_node()
            del node_auto


        base.close()  
        stop_ok = datalayer_system.stop(False)    


# def main():
#     # Create and start ctrlX datalayer...")
#     with ctrlxdatalayer.system.System("") as datalayer_system:
#         datalayer_system.start(False)

#         connectionProvider = "tcp://boschrexroth:boschrexroth@127.0.0.1:2070"
#         if 'SNAP' in os.environ:
#             connectionProvider = "ipc://"

#         print("Connecting", connectionProvider)    

#         # Creating provider...
#         with datalayer_system.factory().create_provider(connectionProvider) as provider:
#             run_provider(provider)

#         datalayer_system.stop(True)


# def run_provider(provider : ctrlxdatalayer.provider.Provider):
#     offset = [0, 0]  #Fetch offsets [queue, history]
#     auto = True 
    
#     db = "file:memdb1?mode=memory&cache=shared" #in-memory database      
#     # db = os.environ.get("SNAP_COMMON") + "/temp.db"
    
#     base = app.utils.initialize(db) #Leave one connection instance open to maintain memory
#     base.execute("pragma journal_mode=wal;")       #Configure database in "write-ahead log" mode

#     node_push = app.nodes.Push(db)  #add job to queue
#     node_pop = app.nodes.Pop(db)    #pop job from queue
#     node_count = app.nodes.Count(db)     #return queue/pending count, write zero to dump
#     node_done =  app.nodes.Done(db)     #add item to db or mark item in db as done
#     node_history = app.nodes.History(db)    #fetch items from history
#     node_auto = app.nodes.Auto(auto)    #automatically generate job orders when true

#     with ctrlxdatalayer.provider_node.ProviderNode(node_push.cbs, 1234) as node,         \
#             ctrlxdatalayer.provider_node.ProviderNode(node_pop.cbs, 1234) as node_2,     \
#             ctrlxdatalayer.provider_node.ProviderNode(node_count.cbs, 1234) as node_3,   \
#             ctrlxdatalayer.provider_node.ProviderNode(node_done.cbs, 1234) as node_4,    \
#             ctrlxdatalayer.provider_node.ProviderNode(node_history.cbs, 1234) as node_5, \
#             ctrlxdatalayer.provider_node.ProviderNode(node_auto.cbs, 1234) as node_6:       
#         result = provider.register_node("mechatronics/job_request", node)
#         if result != ctrlxdatalayer.variant.Result.OK:
#             print("Register job_request failed with: ", result)

#         result = provider.register_node("mechatronics/pop", node_2)
#         if result != ctrlxdatalayer.variant.Result.OK:
#             print("Register pop failed with: ", result)

#         result = provider.register_node("mechatronics/count", node_3)
#         if result != ctrlxdatalayer.variant.Result.OK:
#             print("Register count failed with: ", result)

#         result = provider.register_node("mechatronics/done", node_4)
#         if result != ctrlxdatalayer.variant.Result.OK:
#             print("Register count failed with: ", result)        

#         result = provider.register_node("mechatronics/history", node_5)
#         if result != ctrlxdatalayer.variant.Result.OK:
#             print("Register history failed with: ", result)                

#         result = provider.register_node("mechatronics/auto", node_6)
#         if result != ctrlxdatalayer.variant.Result.OK:
#             print("Register auto failed with: ", result)      

#         print('job-queue starting...')
#         result= provider.start()
#         if result != ctrlxdatalayer.variant.Result.OK:
#             print("Starting job-queue failed with: ", result)
            
#         count=0
#         while True:
#             conn = app.utils.initialize(db)
#             if conn: 
#                 if app.utils.count_queue(conn) == 0  and node_auto.value():
#                     app.utils.add_virtual_job_order(conn, 3)

#                 conn.close()

#             count=count+1
#             if count > 7199:
#                 break

#             time.sleep(5)
        
#         base.close()     #close base database connection

#         result = provider.stop()
 
#         result = provider.unregister_node("mechatronics/job_request")
#         result = provider.unregister_node("mechatronics/pop")
#         result = provider.unregister_node("mechatronics/count")
#         result = provider.unregister_node("mechatronics/done")
#         result = provider.unregister_node("mechatronics/history")



if __name__ == '__main__':
    main()        


    