from pypopush import PypoPush
from threading import Lock
from Queue import Queue

import datetime
import pytest

pytestmark = pytest.mark.skip('skipping entire module')

pypoPush_q = Queue()
telnet_lock = Lock()

@pytest.mark.skip(reason="modify_first_link_cue_point does not exist")
def test_modify_cue_in():
    pp = PypoPush(pypoPush_q, telnet_lock)

    link = pp.modify_first_link_cue_point([])
    assert len(link) == 0

    min_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes = 1)
    link = [{"start":min_ago.strftime("%Y-%m-%d-%H-%M-%S"),
             "cue_in":"0", "cue_out":"30"}]
    link = pp.modify_first_link_cue_point(link)
    assert len(link) == 0

    link = [{"start":min_ago.strftime("%Y-%m-%d-%H-%M-%S"),
             "cue_in":"0", "cue_out":"70"}]
    link = pp.modify_first_link_cue_point(link)
    assert len(link) == 1

