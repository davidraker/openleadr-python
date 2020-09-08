import pytest

from pyopenadr import OpenADRClient, OpenADRServer, enums
from pyopenadr.utils import generate_id
from pyopenadr.messaging import create_message, parse_message
from datetime import datetime, timezone, timedelta

from pprint import pprint
import warnings


@pytest.mark.asyncio
async def test_conformance_008_autocorrect():
    """
    oadrDistributeEvent eventSignal interval durations for a given event MUST
    add up to eiEvent eiActivePeriod duration.
    """
    event_id = generate_id()
    event = {'event_descriptor':
                {'event_id': event_id,
                 'modification_number': 0,
                 'modification_date': datetime.now(),
                 'priority': 0,
                 'market_context': 'MarketContext001',
                 'created_date_time': datetime.now(),
                 'event_status': enums.EVENT_STATUS.FAR,
                 'test_event': False,
                 'vtn_comment': 'No Comment'},
            'active_period':
                {'dtstart': datetime.now(),
                 'duration': timedelta(minutes=5)},
            'event_signals':
                [{'intervals': [{'duration': timedelta(minutes=10),
                                 'signal_payload': 1},
                                {'duration': timedelta(minutes=10),
                                 'signal_payload': 2},
                                {'duration': timedelta(minutes=10),
                                 'signal_payload': 3}],
                  'signal_name': enums.SIGNAL_NAME.SIMPLE,
                  'signal_type': enums.SIGNAL_TYPE.DELTA,
                  'signal_id': generate_id()
                }]
        }

    # Create a message with this event
    with pytest.warns(UserWarning):
        msg = create_message('oadrDistributeEvent',
                             response={'response_code': 200,
                                       'response_description': 'OK',
                                       'request_id': generate_id()},
                             request_id=generate_id(),
                             vtn_id=generate_id(),
                             events=[event])

    parsed_type, parsed_msg = parse_message(msg)
    assert parsed_type == 'oadrDistributeEvent'
    total_time = sum([i['duration'] for i in parsed_msg['events'][0]['event_signals'][0]['intervals']],
                     timedelta(seconds=0))
    assert parsed_msg['events'][0]['active_period']['duration'] == total_time

@pytest.mark.asyncio
async def test_conformance_008_raise():
    """
    oadrDistributeEvent eventSignal interval durations for a given event MUST
    add up to eiEvent eiActivePeriod duration.
    """
    event_id = generate_id()
    event = {'event_descriptor':
                {'event_id': event_id,
                 'modification_number': 0,
                 'modification_date': datetime.now(),
                 'priority': 0,
                 'market_context': 'MarketContext001',
                 'created_date_time': datetime.now(),
                 'event_status': enums.EVENT_STATUS.FAR,
                 'test_event': False,
                 'vtn_comment': 'No Comment'},
            'active_period':
                {'dtstart': datetime.now(),
                 'duration': timedelta(minutes=5)},
            'event_signals':
                [{'intervals': [{'duration': timedelta(minutes=10),
                                 'signal_payload': 1},
                                {'duration': timedelta(minutes=10),
                                 'signal_payload': 2},
                                {'duration': timedelta(minutes=10),
                                 'signal_payload': 3}],
                  'signal_name': enums.SIGNAL_NAME.SIMPLE,
                  'signal_type': enums.SIGNAL_TYPE.DELTA,
                  'signal_id': generate_id()
                },
                {'intervals': [{'duration': timedelta(minutes=1),
                                 'signal_payload': 1},
                                {'duration': timedelta(minutes=2),
                                 'signal_payload': 2},
                                {'duration': timedelta(minutes=2),
                                 'signal_payload': 3}],
                  'signal_name': enums.SIGNAL_NAME.SIMPLE,
                  'signal_type': enums.SIGNAL_TYPE.DELTA,
                  'signal_id': generate_id()
                }]
        }

    with pytest.raises(ValueError):
        msg = create_message('oadrDistributeEvent',
                             response={'response_code': 200,
                                       'response_description': 'OK',
                                       'request_id': generate_id()},
                             request_id=generate_id(),
                             vtn_id=generate_id(),
                             events=[event])