import pytest
import time
import sys
import math
import datetime

from vaping import plugin

config = {
    "type" : "logparse",
    "name" : "logparse_test",
    "exclude" : [
        "exclude"
    ],
    "include" : [
        "include"
    ],
    "fields" : {
        "str_val" : {
            "type": "str",
            "parser" : "str_val=(\S+)"
        },
        "int_val" : {
            "type" : "int",
            "parser": "int_val=(\S+)"
        },
        "float_val" : {
            "type" : "float",
            "parser": "float_val=(\S+)"
        },
        "eval_val" : {
            "type" : "float",
            "eval" : "{int_val}*{float_val}"
        }
    }
}

config_aggr = {
    "type" : "logparse",
    "name" : "logparse_aggr_test",
    "aggregate" : {
        "count" : 10
    },
    "fields" : {
        "int_val" : {
            "type" : "int",
            "parser": "int_val=(\S+)",
            "aggregate" : "sum"
        },
        "float_val" : {
            "type" : "float",
            "parser" : "float_val=(\S+)",
            "aggregate" : "avg"
        },
        "eval_val" : {
            "type" : "float",
            "eval" : "{int_val}/{float_val}",
            "aggregate" : "eval"
        },
        "no_aggr" : {
            "type" : "int",
            "parser" : "int_val=(\S+)"
        }
    }
}


config_time_parser = {
    "type" : "logparse",
    "name" : "logparse_tp_test",
    "fields" : {
        "str_val" : {
            "type": "str",
            "parser" : "str_val=(\S+)"
        }
    },
    "time_parser": {
        "find" : "\d\d\d\d.\d\d.\d\d \d\d:\d\d:\d\d",
        "format" : "%Y.%m.%d %H:%M:%S"
    }
}



@pytest.mark.parametrize("line,result,raises", [
    ("include abcde str_val=xyz int_val=123 float_val=1.23 abcde", {
        "str_val":"xyz", "int_val": 123, "float_val": 1.23,
        "eval_val": 123*1.23}, None),
    ("exclude abcde str_val=xyz int_val=123 float_val=1.23,abcde", {}, None),
    ("include abcde abcde", {}, None)
])
def test_parse_line(line,result,raises):
    inst = plugin.get_instance(config, None)
    if raises:
        with pytest.raises(ValueError) as exception_info:
            _result = inst.parse_line(line)
        assert str(exception_info).find(raises) > -1
    else:
        _result = inst.parse_line(line)
        assert _result == result


@pytest.mark.parametrize("line,iterations,result,raises", [
    ("include abcde int_val=100 float_val=1.0 abcde", 10, [{
        "int_val": 1000, "float_val": 1.0, "eval_val": 1000.0, "no_aggr":100
    }], None),
    ("include abcde int_val=100 float_val=1.0 abcde", 20, [
        {"int_val": 1000 , "float_val": 1.0, "eval_val": 1000.0, "no_aggr":100},
        {"int_val": 1000 , "float_val": 1.0, "eval_val": 1000.0, "no_aggr":100},
    ], None),
    ("include abcde int_val=100 float_val=1.0 abcde", 25, [
        {"int_val": 1000 , "float_val": 1.0, "eval_val": 1000.0, "no_aggr":100},
        {"int_val": 1000 , "float_val": 1.0, "eval_val": 1000.0, "no_aggr":100},
    ], None)

])
def test_aggregate(line, iterations,result,raises):
    inst = plugin.get_instance(config_aggr, None)
    count = config_aggr.get("aggregate").get("count")
    if raises:
        pass
    else:
        messages = []
        for i in range(0, iterations):
            msg = inst.new_message()
            data = {}
            data = inst.process_line(line, data)
            data = inst.process_probe(data)
            msg["data"] = [data]
            messages.append(msg)
        messages = inst.process_messages(messages)

        for row in result:
            row["messages"] = count

        assert len(messages) == math.floor(iterations / count)
        i = 0
        for msg in messages:
            assert msg["data"] == [result[i]]
            i += 1


@pytest.mark.parametrize("line,result,raises", [
    ("2018.12.12 01:02:03 str_val=test", "2018.12.12 01:02:03", None),
    ("2018.12 01:02:03 str_val=test", {}, None)
])
def test_time_parser(line,result,raises):
    inst = plugin.get_instance(config_time_parser, None)
    if raises:
        with pytest.raises(ValueError) as exception_info:
            _result = inst.process_line(line, {})
        assert str(exception_info).find(raises) > -1
    else:
        _result = inst.process_line(line, {})
        if not result:
            assert _result == result
        else:
            dt = datetime.datetime.fromtimestamp(_result["ts"])
            assert dt.strftime("%Y.%m.%d %H:%M:%S") == result



