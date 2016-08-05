
import logging
import pytest
from vaping.plugins import sflowtool


def test_parsing():
    tests = [
        {
        'line': 'CNTR,10.41.110.11,563,6,10000000000,1,3,57860653709549,3111366693,5115419,0,0,0,0,21535236293279,679349160,150746,2373632768,0,0,0',
        'expected': {
            'type': 'CNTR',
            'agent': '10.41.110.11',
            'status': 3,
            'ifspeed': 10000000000,
            'direction': 1,
            'prom_mode': 0,
            'iftyp': 6,
            'ifidx': 563,

            'in_oct': 57860653709549,
            'in_ucast': 3111366693,
            'in_mcast': 5115419,
            'in_bcast': 0,
            'in_unk_proto': 0,
            'in_err': 0,
            'in_discard': 0,
            'out_oct': 21535236293279,
            'out_ucast': 679349160,
            'out_mcast': 150746,
            'out_bcast': 2373632768,
            'out_err': 0,
            'out_discard': 0,
            },
        },
    ]

    for each in tests:
        assert each['expected'] == sflowtool.parse_line(each['line'])



def test_calc_rate():
#datetime.datetime.strptime('2016-01-14 07:35:16.196352', "%Y-%m-%d %H:%M:%S.%f")
    pass

