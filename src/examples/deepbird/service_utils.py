#!/usr/bin/env python3
# Copyright 2021 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Heavily inspired, even copied from the utilities used to build the
# Joy Detection Demo.

import queue
import threading

class Service:
    """
    An abstract class used to build services which can be started, stopped and
    manage a queue of requests.

    Subclasses should implement the process method to do work, while clients
    should call submit to schedule it. Since this class is a ContextManager
    subclasses can be used in 'with' statements'
    """
    def __init__(self):
        self._requests = queue.Queue()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while True:
            request = self._requests.get()
            if request is None:
                self.shutdown()
                break
            self.process(request)
            self._requests.task_done()

    def process(self, request):
        """
        Implemented by subclasses to do the particular work of the service
        """
        pass

    def shutdown(self):
        """Implemented by subclasses take care of any clean up after the last
request is processed."""
        pass

    def submit(self, request):
        self._requests.put(request)

    def close(self):
        self._requests.put(None)
        self._thread.join()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()

def main():
    """Example on how to use the Service class."""
    class MyService(Service):
        def process(self, request):
            print("Processing %s" % request)
        def shutdown(self):
            print("Shutting down")
            
    with MyService() as my_service:
        my_service.submit("Hello")
        my_service.submit("World")
        
if __name__ == "__main__":
    main()