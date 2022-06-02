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

import ctrlxdatalayer
from ctrlxdatalayer.provider_node import ProviderNodeCallbacks, NodeCallback
from ctrlxdatalayer.variant import Result, Variant

from comm.datalayer import NodeClass

import json
# import time
import os
# import sqlite3
from sqlite3 import Error
from jsonschema import validate

import app.utils

class Push:
    # dataString: str = "Hello from Python Provider"
    id : int = 0

    schema = {
        "type" : "object",
        "properties" : {
            "name" : {"type" : "array"},
            "email" : {"type" : "string"},
            "color" : {"type" : "array"},
        },
        "required" : ["name", "email", "color"]
    }
    
    def __init__(self, provider: ctrlxdatalayer.provider, db):
        self.cbs = ProviderNodeCallbacks(
        self.__on_create,
        self.__on_remove,
        self.__on_browse,
        self.__on_read,
        self.__on_write,
        self.__on_metadata
        )
        self.providerNode = ctrlxdatalayer.provider_node.ProviderNode(self.cbs)

        self.db = db
        self.provider = provider

        self.name = "job_request"
        self.address = "mechatronics/job_request"
        self.description = 'Write job (json format) to add to pending jobs'

        self.metadata = self.create_metadata("types/datalayer/string", self.name, '', self.description)
        
    def register_node(self):
        return self.provider.register_node(self.address, self.providerNode)

    def unregister_node(self):
        self.provider.unregister_node(self.address)

    def create_metadata(self, typeAddress: str, name: str, unit: str, description: str):

        return ctrlxdatalayer.metadata_utils.MetadataBuilder.create_metadata(
            name, description, unit, description+"_url", NodeClass.NodeClass.Variable,
            read_allowed=True, write_allowed=True, create_allowed=False, delete_allowed=False, browse_allowed=True,
           type_path=typeAddress)        

    def __on_create(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        # self.dataString
        cb(Result.OK, None)

    def __on_remove(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        # Not implemented because no wildcard is registered
        cb(Result.UNSUPPORTED, None)

    def __on_browse(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        new_data = Variant()
        new_data.set_array_string([])
        cb(Result.OK, new_data)

    def __on_read(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        _data = Variant()

        conn = app.utils.initialize(self.db)
        if conn:
            _data.set_string(json.dumps(app.utils.fetch_queue(conn, 50, 0))) 
            conn.close()

        cb(Result.OK, _data)
    
    def __on_write(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        _test = json.loads(data.get_string())
        # _isValid = validate(_test, self.schema)
 
        conn = app.utils.initialize(self.db)
        if conn: # and _isValid:
            app.utils.add_job_order(conn, json.dumps(_test))
            conn.close()

        cb(Result.OK, None)        

    def __on_metadata(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        cb(Result.OK, self.metadata)  

class Pop:
    _value: str = ""
    
    def __init__(self, provider: ctrlxdatalayer.provider, db):
        self.cbs = ProviderNodeCallbacks(
        self.__on_create,
        self.__on_remove,
        self.__on_browse,
        self.__on_read,
        self.__on_write,
        self.__on_metadata
        )
        self.providerNode = ctrlxdatalayer.provider_node.ProviderNode(self.cbs)

        self.db = db
        self.provider = provider

        self.name = "pop"
        self.address = "mechatronics/pop"
        self.description = 'Write 1 to pop next job from queue'

        self.metadata = self.create_metadata("types/datalayer/string", self.name, '', self.description)
        
    def register_node(self):
        return self.provider.register_node(self.address, self.providerNode)

    def unregister_node(self):
        self.provider.unregister_node(self.address)

    def create_metadata(self, typeAddress: str, name: str, unit: str, description: str):

        return ctrlxdatalayer.metadata_utils.MetadataBuilder.create_metadata(
            name, description, unit, description+"_url", NodeClass.NodeClass.Variable,
            read_allowed=True, write_allowed=True, create_allowed=False, delete_allowed=False, browse_allowed=True,
           type_path=typeAddress)           

    def __on_create(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        self.dataString
        cb(Result(Result.OK), None)

    def __on_remove(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        # Not implemented because no wildcard is registered
        cb(Result(Result.UNSUPPORTED), None)

    def __on_browse(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        new_data = Variant()
        new_data.set_array_string([])
        cb(Result(Result.OK), new_data)

    def __on_read(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        _data = Variant()  
        _data.set_string(self._value)
           
        cb(Result(Result.OK), _data)
    
    def __on_write(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        _data = Variant()
   
        conn = app.utils.initialize(self.db)
        if conn and int(data.get_string()) == 1:  #modified 14.06 for testing
            self._value = json.dumps(app.utils.pop(conn))
            _data.set_string(self._value)
        
        if conn: 
            conn.close()

        cb(Result(Result.OK), _data)        

    def __on_metadata(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        cb(Result.OK, self.metadata)      

class Count:
    data: int = 0
    
    def __init__(self, provider: ctrlxdatalayer.provider, db):
        self.cbs = ProviderNodeCallbacks(
        self.__on_create,
        self.__on_remove,
        self.__on_browse,
        self.__on_read,
        self.__on_write,
        self.__on_metadata
        )
        self.providerNode = ctrlxdatalayer.provider_node.ProviderNode(self.cbs)

        self.db = db
        self.provider = provider

        self.name = "count"
        self.address = "mechatronics/count"
        self.description = 'Number of pending jobs in queue.  Write 0 to clear queue.'

        self.metadata = self.create_metadata("types/datalayer/int32", self.name, '', self.description)
        
    def register_node(self):
        return self.provider.register_node(self.address, self.providerNode)

    def unregister_node(self):
        self.provider.unregister_node(self.address)

    def create_metadata(self, typeAddress: str, name: str, unit: str, description: str):

        return ctrlxdatalayer.metadata_utils.MetadataBuilder.create_metadata(
            name, description, unit, description+"_url", NodeClass.NodeClass.Variable,
            read_allowed=True, write_allowed=True, create_allowed=False, delete_allowed=False, browse_allowed=True,
           type_path=typeAddress)   

    def __on_create(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        print("__on_create")
        self.data
        cb(Result(Result.OK), None)

    def __on_remove(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        # Not implemented because no wildcard is registered
        cb(Result(Result.UNSUPPORTED), None)

    def __on_browse(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        _data = Variant()
        _data.set_array_string([])
        cb(Result(Result.OK), _data)

    def __on_read(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        _data = Variant()

        conn = app.utils.initialize(self.db)
        if conn:
            _data.set_uint32(app.utils.count_queue(conn))
            conn.close()

        cb(Result(Result.OK), _data)
    
    def __on_write(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        conn = app.utils.initialize(self.db)
        if conn and data.get_uint32() == 0:
            app.utils.dump(conn)
        
        if conn: 
            conn.close()

        cb(Result(Result.OK), None)

    def __on_metadata(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        cb(Result.OK, self.metadata)            

class Done:
    _value: str = ""
    
    def __init__(self, provider: ctrlxdatalayer.provider, db):
        self.cbs = ProviderNodeCallbacks(
        self.__on_create,
        self.__on_remove,
        self.__on_browse,
        self.__on_read,
        self.__on_write,
        self.__on_metadata
        )
        self.providerNode = ctrlxdatalayer.provider_node.ProviderNode(self.cbs)

        self.db = db
        self.provider = provider

        self.name = "done"
        self.address = "mechatronics/done"
        self.description = 'Write id value to update time_out timestamp in history table'

        self.metadata = self.create_metadata("types/datalayer/string", self.name, '', self.description)
        
    def register_node(self):
        return self.provider.register_node(self.address, self.providerNode)

    def unregister_node(self):
        self.provider.unregister_node(self.address)

    def create_metadata(self, typeAddress: str, name: str, unit: str, description: str):

        return ctrlxdatalayer.metadata_utils.MetadataBuilder.create_metadata(
            name, description, unit, description+"_url", NodeClass.NodeClass.Variable,
            read_allowed=True, write_allowed=True, create_allowed=False, delete_allowed=False, browse_allowed=True,
           type_path=typeAddress)   

    def __on_create(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        self.data
        cb(Result(Result.OK), None)

    def __on_remove(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        # Not implemented because no wildcard is registered
        cb(Result(Result.UNSUPPORTED), None)

    def __on_browse(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        _data = Variant()
        _data.set_array_string([])
        cb(Result(Result.OK), _data)

    def __on_read(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        _data = Variant()  
        _data.set_string(self._value)
           
        cb(Result(Result.OK), _data)
    
    def __on_write(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        _data = Variant() 

        conn = app.utils.initialize(self.db)
        if conn and int(data.get_string()) > 0:  #modified 14.06 for testing
            self._value = json.dumps(app.utils.done(conn, data.get_string()))
            _data.set_string(self._value)           
        
        if conn: 
            conn.close()

        cb(Result(Result.OK), _data)

    def __on_metadata(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        cb(Result.OK, self.metadata)            

class History:
    _value: str = ""
    
    def __init__(self, provider: ctrlxdatalayer.provider, db):
        self.cbs = ProviderNodeCallbacks(
        self.__on_create,
        self.__on_remove,
        self.__on_browse,
        self.__on_read,
        self.__on_write,
        self.__on_metadata
        )
        self.providerNode = ctrlxdatalayer.provider_node.ProviderNode(self.cbs)

        self.db = db
        self.provider = provider

        self.name = "history"
        self.address = "mechatronics/history"
        self.description = 'Job history listing'

        self.metadata = self.create_metadata("types/datalayer/string", self.name, '', self.description)
        
    def register_node(self):
        return self.provider.register_node(self.address, self.providerNode)

    def unregister_node(self):
        self.provider.unregister_node(self.address)

    def create_metadata(self, typeAddress: str, name: str, unit: str, description: str):

        return ctrlxdatalayer.metadata_utils.MetadataBuilder.create_metadata(
            name, description, unit, description+"_url", NodeClass.NodeClass.Variable,
            read_allowed=True, write_allowed=False, create_allowed=False, delete_allowed=False, browse_allowed=True,
           type_path=typeAddress)   

    def __on_create(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        self.data
        cb(Result(Result.OK), None)

    def __on_remove(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        # Not implemented because no wildcard is registered
        cb(Result(Result.UNSUPPORTED), None)

    def __on_browse(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        _data = Variant()
        _data.set_array_string([])
        cb(Result(Result.OK), _data)

    def __on_read(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        _data = Variant()

        conn = app.utils.initialize(self.db)
        if conn:
            _data.set_string(json.dumps(app.utils.fetch_history(conn, 50, 0))) 
            conn.close()

        cb(Result(Result.OK), _data)
    
    def __on_write(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        cb(Result(Result.OK), None)

    def __on_metadata(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        cb(Result.OK, self.metadata)  

class Auto:
     
    def __init__(self, provider: ctrlxdatalayer.provider, auto):
        self.cbs = ProviderNodeCallbacks(
        self.__on_create,
        self.__on_remove,
        self.__on_browse,
        self.__on_read,
        self.__on_write,
        self.__on_metadata
        )


        self.providerNode = ctrlxdatalayer.provider_node.ProviderNode(self.cbs)
        self.auto = auto
        self.provider = provider

        self.name = "auto"
        self.address = "mechatronics/auto"
        self.description = 'Enable to auto-generate virtual jobs'

        self.metadata = self.create_metadata("types/datalayer/bool8", self.name, '', self.description)
        
    def register_node(self):
        return self.provider.register_node(self.address, self.providerNode)

    def unregister_node(self):
        self.provider.unregister_node(self.address)

    def create_metadata(self, typeAddress: str, name: str, unit: str, description: str):

        return ctrlxdatalayer.metadata_utils.MetadataBuilder.create_metadata(
            name, description, unit, description+"_url", NodeClass.NodeClass.Variable,
            read_allowed=True, write_allowed=True, create_allowed=False, delete_allowed=False, browse_allowed=True,
           type_path=typeAddress)           

    def __on_create(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        cb(Result(Result.OK), None)

    def __on_remove(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        # Not implemented because no wildcard is registered
        cb(Result(Result.UNSUPPORTED), None)

    def __on_browse(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        _data = Variant()
        _data.set_array_string([])
        cb(Result(Result.OK), _data)

    def __on_read(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        _data = Variant()
        _data.set_bool8(self.auto) 
        cb(Result(Result.OK), _data)
    
    def __on_write(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        self.auto = data.get_bool8()
        cb(Result(Result.OK), None)

    def __on_metadata(self, userdata: ctrlxdatalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        cb(Result.OK, self.metadata)  

    def value(self):
        return self.auto          