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

import datalayer.clib
from datalayer.provider_node import ProviderNodeCallbacks, NodeCallback
from datalayer.variant import Result, Variant

import json

class NodePush:
    dataString: str = "Hello from Python Provider"
    
    def __init__(self, queue):
        self.cbs = ProviderNodeCallbacks(
        self.__on_create,
        self.__on_remove,
        self.__on_browse,
        self.__on_read,
        self.__on_write,
        self.__on_metadata
        )
        self.queue = queue

    def __on_create(self, userdata: datalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        print("__on_create")
        self.dataString
        cb(Result(Result.OK), None)

    def __on_remove(self, userdata: datalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        # Not implemented because no wildcard is registered
        print("__on_remove")
        cb(Result(Result.UNSUPPORTED), None)

    def __on_browse(self, userdata: datalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        print("__on_browse")
        new_data = Variant()
        new_data.set_array_string([])
        cb(Result(Result.OK), new_data)

    def __on_read(self, userdata: datalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        print("bostroemc: __on_read", userdata)
        new_data = Variant()
        new_data.set_string(json.dumps(self.queue))
        cb(Result(Result.OK), new_data)
    
    def __on_write(self, userdata: datalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        print("bostroemc: __on_write", data.get_string())
        self.queue.append(data.get_string())
        cb(Result(Result.OK), None)

    def __on_metadata(self, userdata: datalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        print("__on_metadata")
        cb(Result(Result.OK), None)

class NodePop:
    dataString: str = "Hello from Python Provider"
    
    def __init__(self, queue):
        self.cbs = ProviderNodeCallbacks(
        self.__on_create,
        self.__on_remove,
        self.__on_browse,
        self.__on_read,
        self.__on_write,
        self.__on_metadata
        )
        self.queue = queue

    def __on_create(self, userdata: datalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        print("__on_create")
        self.dataString
        cb(Result(Result.OK), None)

    def __on_remove(self, userdata: datalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        # Not implemented because no wildcard is registered
        print("__on_remove")
        cb(Result(Result.UNSUPPORTED), None)

    def __on_browse(self, userdata: datalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        print("__on_browse")
        new_data = Variant()
        new_data.set_array_string([])
        cb(Result(Result.OK), new_data)

    def __on_read(self, userdata: datalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        print("bostroemc: __on_read", userdata)
        new_data = Variant()
        new_data.set_string(json.dumps(self.queue[0]))
        cb(Result(Result.OK), new_data)
    
    def __on_write(self, userdata: datalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        print("bostroemc: __on_write", data.get_string())
        new_data = Variant()
        new_data.set_string(json.dumps(self.queue[0]))
        self.queue.pop(0)
        cb(Result(Result.OK), new_data)

    def __on_metadata(self, userdata: datalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        print("__on_metadata")
        cb(Result(Result.OK), None)        