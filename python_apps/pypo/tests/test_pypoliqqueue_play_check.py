from pypoliqqueue import PypoLiqQueue
from pypoliquidsoap import PypoLiquidsoap
from pypopush import PypoPush
from telnetliquidsoap import DummyTelnetLiquidsoap, TelnetLiquidsoap

from Queue import Queue
from threading import Lock
from threading import Thread
import pprint

import os
import re
import sys
import signal
import logging
import time
import mutagen
from datetime import datetime
from datetime import timedelta

from configobj import ConfigObj

def keyboardInterruptHandler(signum, frame):
    logger = logging.getLogger()
    logger.info('\nKeyboard Interrupt\n')
    sys.exit(0)
signal.signal(signal.SIGINT, keyboardInterruptHandler)

config = ConfigObj('/etc/airtime/airtime.conf')

# configure logging
format = '%(levelname)s - %(pathname)s - %(lineno)s - %(asctime)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=format, stream=sys.stdout)
logging.captureWarnings(True)

ls_host = config['pypo']['ls_host']
ls_port = config['pypo']['ls_port']
logger = logging.getLogger()

telnet_lock = Lock()
pypoPush_q = Queue()

pypo_liquidsoap = PypoLiquidsoap(logger, telnet_lock,\
            ls_host, ls_port)

pp = PypoPush(pypoPush_q, telnet_lock, pypo_liquidsoap, config['pypo'])
pp.daemon = True
pp.start()

def is_playing(media_item):
    print "%s: Current liquidsoap contents: %s"% (datetime.utcnow(), pypo_liquidsoap.liq_queue_tracker)
    is_playing = False
    for i in pypo_liquidsoap.liq_queue_tracker:
        mi = pypo_liquidsoap.liq_queue_tracker[i]
        if mi != None and media_item['end'] == mi['end'] and media_item['start'] == mi['start'] and media_item['id'] == mi['id']:
            return True
    return False

def requeue( interval, queueobj, sched, timeoffset ):
    print "Reinserting previous sched after %s secs" % (interval + timeoffset)
    print "Previous sched: %s" % sched
    time.sleep(interval + timeoffset)
    print "Inserting sched: %s" % sched
    queueobj.put(sched)

def date_interval_to_seconds_withneg(interval):
    """
    Convert timedelta object into int representing the number of seconds.
    """
    seconds = (interval.microseconds + \
               (interval.seconds + interval.days * 24 * 3600) * 10 ** 6) / float(10 ** 6)
    return seconds

def check_playback(media_schedule, caplog):
    currecord = 0
    numplays = 0
    keys = sorted(media_schedule.keys())

    for k in keys:
        print k.strftime("%Y-%m-%d %H:%M:%S")
        print media_schedule[k]
        matched = False

        print "Searching through log record %s to %s" % (currecord, len(caplog.records))
        for i in range(currecord, len(caplog.records)):
            record = caplog.records[i]

            if record.filename == "telnetliquidsoap.py":
                try:
                    result = re.search('s[0-9].push.+media_id="([0-9]+)".+schedule_table_id="([0-9]+)".+":(.+)', record.msg)
                    media_id = result.group(1)
                    row_id = result.group(2)
                    file = result.group(3)
                    print "Played at " + record.asctime[:19] + " media_id=" + media_id + " row_id=" + row_id + " file=" + file
                    matched = True
                    currecord = i + 1
                    numplays += 1
                    break
                except AttributeError:
                    # Reg exp not matched
                    pass

        if matched:
            assert k.strftime("%Y-%m-%d %H:%M:%S") == record.asctime[:19], "Media should have played at %s" % k.strftime("%Y-%m-%d %H:%M:%S")
            assert int(media_id) == media_schedule[k]['id'], "Media ID %s should have played at %s" % (media_schedule[k]['id'], k.strftime("%Y-%m-%d %H:%M:%S"))
            assert int(row_id) == media_schedule[k]['row_id'], "Row ID %s should have played at %s" % (media_schedule[k]['row_id'], k.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            assert False, "Media scheduled at %s file %s did not play" % (k.strftime("%Y-%m-%d %H:%M:%S"), media_schedule[k]['dst'])

    # Read the rest of the caplog to check for stray playbacks
    for i in range(currecord, len(caplog.records)):
        record = caplog.records[i]
        print "Current record #" + str(i)
        if record.filename == "telnetliquidsoap.py":
            try:
                result = re.search('s[0-9].push.+media_id="([0-9]+)".+schedule_table_id="([0-9]+)".+":(.+)', record.msg)
                media_id = result.group(1)
                print "Record#" + str(i) + ": Played at " + record.asctime[:19] + " media_id=" + media_id + " row_id=" + row_id + " file=" + file
                numplays += 1
            except AttributeError:
                # Reg exp not matched
                pass

    assert numplays == len(media_schedule)

def test_pypoliqqueue_play_check(caplog):

    print "\nTime now: %s" % datetime.utcnow()

    media_schedule = {}

    now = datetime.utcnow()

    audioPath1 = os.path.abspath("audio_1.mp3")
    m = mutagen.File(audioPath1, easy=True)
    length1 = round(getattr(m.info, 'length', 0.0), 3)

    start_dt_1 = now + timedelta(seconds=5)
    end_dt_1 = start_dt_1 + timedelta(seconds=length1)

    media_schedule[start_dt_1] = {"id": 55, \
            "type":"file", \
            "row_id":1, \
            "uri":"", \
            "dst":audioPath1, \
            "fade_in":0, \
            "fade_out":0, \
            "cue_in":0, \
            "cue_out":length1, \
            "file_ready":True, \
            "start": start_dt_1, \
            "end": end_dt_1, \
            "show_name":"Test Show 1", \
            "replay_gain": 0, \
            "independent_event": True \
            }

    audioPath2 = os.path.abspath("audio_2.mp3")
    m = mutagen.File(audioPath2, easy=True)
    length2 = round(getattr(m.info, 'length', 0.0), 3)

    start_dt_2 = end_dt_1
    end_dt_2 = start_dt_2 + timedelta(seconds=length2)

    media_schedule[start_dt_2] = {"id": 56, \
            "type":"file", \
            "row_id":2, \
            "uri":"", \
            "dst":audioPath2, \
            "fade_in":0, \
            "fade_out":0, \
            "cue_in":0, \
            "cue_out":length2, \
            "file_ready":True, \
            "start": start_dt_2, \
            "end": end_dt_2, \
            "show_name":"Test Show 1", \
            "replay_gain": 0, \
            "independent_event": True \
            }

    audioPath3 = os.path.abspath("audio_1.mp3")
    m = mutagen.File(audioPath3, easy=True)
    length3 = round(getattr(m.info, 'length', 0.0), 3)

    start_dt_3 = end_dt_2
    end_dt_3 = start_dt_3 + timedelta(seconds=length3)

    media_schedule[start_dt_3] = {"id": 57, \
            "type":"file", \
            "row_id":3, \
            "uri":"", \
            "dst":audioPath3, \
            "fade_in":0, \
            "fade_out":0, \
            "cue_in":0, \
            "cue_out":length3, \
            "file_ready":True, \
            "start": start_dt_3, \
            "end": end_dt_3, \
            "show_name":"Test Show 1", \
            "replay_gain": 0, \
            "independent_event": True \
            }

    audioPath4 = os.path.abspath("audio_2.mp3")
    m = mutagen.File(audioPath3, easy=True)
    length4 = round(getattr(m.info, 'length', 0.0), 3)

    start_dt_4 = end_dt_3
    end_dt_4 = start_dt_4 + timedelta(seconds=length3)

    media_schedule[start_dt_4] = {"id": 58, \
            "type":"file", \
            "row_id":4, \
            "uri":"", \
            "dst":audioPath4, \
            "fade_in":0, \
            "fade_out":0, \
            "cue_in":0, \
            "cue_out":length4, \
            "file_ready":True, \
            "start": start_dt_4, \
            "end": end_dt_4, \
            "show_name":"Test Show 1", \
            "replay_gain": 0, \
            "independent_event": True \
            }

    pypoPush_q.put(media_schedule)

    print "schedule:"
    print pprint.pformat(media_schedule)
    print "start_dt_1: %s" % start_dt_1

    wait_time = date_interval_to_seconds_withneg(media_schedule[start_dt_1]['start'] - datetime.utcnow())
    print "%s: Wait %s secs until 1st media plays.." % (datetime.utcnow(), wait_time)

    time.sleep(wait_time + 1) #Add 1 second just to make sure the media already started playing

    wait_time = date_interval_to_seconds_withneg(media_schedule[start_dt_2]['start'] - datetime.utcnow())
    
    # Start a new thread for the purpose of requeuing the same sched just before the 2nd track plays
    Thread(target = requeue, args=[wait_time, pp.future_scheduled_queue, media_schedule, 0.1]).start()

    print "%s: Wait %s secs until 2nd media plays.." % (datetime.utcnow(), wait_time)
    time.sleep(wait_time + 1) #Add 1 second just to make sure the media already started playing


    wait_time = date_interval_to_seconds_withneg(media_schedule[start_dt_4]['end'] - datetime.utcnow())
    time.sleep(wait_time + 1) #Add 1 second just to make sure the media already started playing

    check_playback( media_schedule, caplog)






