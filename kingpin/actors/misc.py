# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Copyright 2014 Nextdoor.com, Inc

"""Misc Actor objects.

These are common utility Actors that don't really need their own
dedicated packages. Things like sleep timers, loggers, etc.
"""

import logging
import time

from tornado import gen
from tornado import ioloop

from kingpin.actors import base
from kingpin.actors import exceptions

log = logging.getLogger(__name__)

__author__ = 'Matt Wise <matt@nextdoor.com>'


class Sleep(base.BaseActor):
    """Simple actor that just sleeps for an arbitrary amount of time."""

    def __init__(self, *args, **kwargs):
        """Initializes the Actor.

        Args:
            desc: String description of the action being executed.
            options: Dictionary with the following settings:
              { 'sleep': <int of time to sleep> }
        """
        super(Sleep, self).__init__(*args, **kwargs)

        if 'sleep' not in self._options:
            raise exceptions.InvalidOptions('Missing "sleep" option.')

        self._sleep = self._options['sleep']

    @gen.coroutine
    def _execute(self):
        """Executes an actor and yields the results when its finished.

        raises: gen.Return(True)
        """
        log.debug('[%s] Sleeping for %s seconds' % (self._desc, self._sleep))
        yield gen.Task(
            ioloop.IOLoop.current().add_timeout,
            time.time() + self._sleep)

        raise gen.Return(True)
