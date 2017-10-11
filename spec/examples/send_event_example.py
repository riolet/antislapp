# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
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

import os.path
import sys

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

CLIENT_ACCESS_TOKEN = os.environ.get('CLIENT_TOKEN', 'YOUR_ACCESS_TOKEN')


# This example sends an event request to the AI server, and reports the response.
# If the event name matches an intent that has that event name as a trigger,
# The response text/speech will be the response of that intent firing.


def main():
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

    request = ai.event_request(apiai.events.Event("hangman-program"))

    request.lang = 'en'  # optional, default value equal 'en'

    request.session_id = "b3e7146acd1f9e3a4f3c05a5e1d850a3054b"

    response = request.getresponse()

    print (response.read())


if __name__ == '__main__':
    main()
