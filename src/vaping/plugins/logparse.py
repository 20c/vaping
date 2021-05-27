import datetime
import re

import confu.schema

import vaping
import vaping.config
from vaping.plugins import PluginConfigSchema


class FieldSchema(confu.schema.Schema):
    parser = confu.schema.Str(
        help="Regex pattern to parse field value, needs to one group in it"
    )
    type = confu.schema.Str(help="Value type (int, float etc.)")
    aggregate = confu.schema.Str(
        help="How to aggregate the field if aggregation is turned on (sum, avg, eval)"
    )
    eval = confu.schema.Str(
        help="Evaluate to create the value, other fields' values will be available in the string formatting"
    )


class TimeParserSchema(confu.schema.Schema):
    find = confu.schema.Str(help="Regex string to find timestamps.")
    format = confu.schema.Str(help="Datetime format to output timestamps.")


class AggregateSchema(confu.schema.Schema):
    count = confu.schema.Int(help="Aggregate n lines")


class LogParseSchema(PluginConfigSchema):
    """
    Define a schema for FPing and also define defaults.
    """

    fields = confu.schema.Dict(item=FieldSchema(), default={}, help="Field definition")
    time_parser = TimeParserSchema(
        help="If specified will be passed to strptime to generate a timestamp from the logline"
    )
    exclude = confu.schema.List(
        item=confu.schema.Str(),
        default=[],
        help="list of regex patterns that will cause lines to be excluded on match",
    )
    include = confu.schema.List(
        item=confu.schema.Str(),
        default=[],
        help="list of regex patterns that will cause lines to be included on match",
    )
    aggregate = AggregateSchema(default={}, help="aggregation config")


@vaping.plugin.register("logparse")
class LogParse(vaping.plugins.FileProbe):
    r"""
    Log parse plugin base

    Will parse a log line by line and probe to emit data
    over a specified interval.

    # Config

    - path (`str`): log file path
    - fields (`dict`): field definition

        field name as key

        `parser` regex pattern to parse field value, needs to
            one group in it

        `type` value type (int, float etc.)

        `aggregate` how to aggregate the field if aggregation
            is turned on (sum, avg, eval)

        `eval` evaluate to create the value, other fields
            values will be available in the string formatting

    - time_parser (`dict`) if specified will be passed to strptime to
    generate a timestamp from the logline

    ```
    time_parser:
        find: \d\d:\d\d:\d\d
        format: %H:%M:%S
    ```
    - exclude (`list`): list of regex patterns that will cause
      lines to be excluded on match
    - include (`list`): list of regex patterns that will cause
      lines to be included on match
    - aggregate (`dict`): aggregation config
        -`count` aggregate n lines

    # Instance Attributes

    - stack (`list`)
    - fields (`dict`): field config
    - aggregate_count (`int`)
    - exclude (`list`)
    - include (`list`)
    - time_parser (`dict`)
    """

    # default_config = {"fields": {}, "exclude": [], "include": [], "aggregate": {}}

    ConfigSchema = LogParseSchema

    def init(self):
        self.stack = []
        self.fields = self.config.get("fields")
        self.aggregate_count = self.config.get("aggregate").get("count", 0)
        self.exclude = self.config.get("exclude", [])
        self.include = self.config.get("include", [])
        self.time_parser = self.config.get("time_parser")

    def parse_line(self, line):
        """
        Here is where we parse values out of a single line read from the log
        and return a dict containg keys and values

        **Arguments**

        - line (`str`)
        """

        # if a list of exclude patterns is specified
        # check if the line matches any of them
        # and ignore it if it does
        if self.exclude:
            for pattern in self.exclude:
                if re.search(pattern, line):
                    return {}

        # if a list of include patterns is specified
        # check if the line matches any of them
        # and ignore it if it does not
        if self.include:
            matched = False
            for pattern in self.include:
                if re.search(pattern, line):
                    matched = True
                    break
            if not matched:
                return {}

        fields = self.config.get("fields", {})

        data = {}

        for k, v in list(fields.items()):
            try:
                data[k] = self.parse_field_value(v, line)
            except (ValueError, TypeError) as exc:
                self.log.debug(str(exc))
                return {}

        for k, v in list(fields.items()):
            if "eval" in v:
                data[k] = eval(v["eval"].format(**data))
            if "type" in v:
                data[k] = self.validate_value(data[k], v["type"])

            # print(k, data[k])

        return data

    def parse_field_value(self, field, line):
        """
        takes a field definition and a log line and
        attempts to parse out the field's value
        """

        value = None

        # parse field value
        if "parser" in field:
            match = re.search(field["parser"], line)
            if not match:
                raise ValueError(f"Could not parse field value {field}\n{line}")
            value = match.group(1)

        # apply field type
        if "type" in field and value is not None:
            value = self.validate_value(value, field["type"])

        return value

    def validate_value(self, value, typ):
        try:
            return __builtins__.get(typ).__call__(value)
        except AttributeError:
            validate = getattr(self, f"validate_{typ}", None)
            if validate:
                value = validate(value)
            else:
                raise

    def validate_elapsed(self, value):
        return self.validate_interval(value)

    def validate_interval(self, value):
        """
        validates a string describing elapsed time or time duration

        **Arguments**

        - value (`str`): elapsed time (example: 1d2h)

        **Returns**

        seconds (`float`)
        """
        return vaping.config.parse_interval(value)

    def aggregate(self, messages):

        """
        Takes a list of messages and aggregates them
        according to aggration config

        **Arguments**

        - messagges (`list<dict>`)

        **Returns**

        list of aggregated messages (`list<dict>`)
        """

        # aggregation is not turned on, just return
        # the messages as they are
        if not self.aggregate_count:
            return messages

        rv = []

        # push messages onto stack
        self.stack = self.stack + messages

        # stack is still smaller than the aggregation count
        # return empty list
        if len(self.stack) < self.aggregate_count:
            return rv

        # while stack is bigger than the aggregation count
        # pop messages off the stack and aggregate
        while len(self.stack) >= self.aggregate_count:

            # pop first message in stack
            message = self.stack[0]
            self.stack.remove(self.stack[0])

            # join data of other messages to first message
            # no aggregation yet
            for other in self.stack[: self.aggregate_count - 1]:
                message["data"].extend(other["data"])
                self.stack.remove(self.stack[0])

            # append multi-data message to result
            rv.append(message)

        # aggregate
        for message in rv:
            self.aggregate_message(message)

        return rv

    def aggregate_message(self, message):
        """
        Takesa vaping message with multiple items
        in it's data property and aggregates that data

        **Arguments**

        - message (`dict`): vaping message dict
        """

        # first data point is the main data point
        main = message["data"][0]

        # finalizers are applied after initial aggregation
        # we keep track of them here
        # TODO: move to class property
        finalizers = ["eval"]

        # aggregate
        for k, v in list(self.fields.items()):
            if v.get("aggregate") not in finalizers:
                main[k] = self.aggregate_field(k, message["data"])

        # aggregate finalizers
        for k, v in list(self.fields.items()):
            if v.get("aggregate") in finalizers:
                main[k] = self.aggregate_field(k, message["data"])

        # store number of aggregated messages in message data
        # at the `messages` key
        main["messages"] = len(message["data"])

        # remove everything but the main data point from
        # the message
        message["data"] = [main]

    def aggregate_field(self, field_name, rows):
        """
        takes a field name and a set of rows and will
        return an aggregated value

        this requires for the field to have it's `aggregate`
        config specified in the probe config

        **Arguments**

        - field_name (`str`)
        - rows (`list`)

        **Returns**

        aggregated value
        """

        field = self.fields.get(field_name, {})

        # no aggregator specified in field config
        # return the value of the last row as is
        if "aggregate" not in field:
            return rows[-1][field_name]

        # get aggregate function
        aggregate = getattr(self, "aggregate_{}".format(field.get("aggregate")))

        r = aggregate(field_name, rows)
        return r

    def aggregate_sum(self, field_name, rows):
        """
        Aggregate sum

        **Arguments**

        - field_name (`str`): field to aggregate
        - rows (`list`): list of vaping message data rows

        **Returns**

        sum
        """
        c = 0
        for row in rows:
            c = c + row.get(field_name, 0)
        return c

    def aggregate_eval(self, field_name, rows):
        """
        Aggregate using an `eval()` result

        Needs to have `eval` set in the field config. Value will
        be passed straight to the `eval()` function so caution is
        advised.

        **Arguments**

        - field_name (`str`): field to aggregate
        - rows (`list`): list of vaping message data rows

        **Returns**

        eval result
        """
        return eval(self.fields[field_name].get("eval").format(**rows[0]))

    def aggregate_avg(self, field_name, rows):
        """
        Aggregate average value

        **Arguments**

        - field_name (`str`): field to aggregate
        - rows (`list`): list of vaping message data rows

        **Returns**

        avg (`float`)
        """
        return self.aggregate_sum(field_name, rows) / len(rows)

    def parse_time(self, line):
        find = self.time_parser.get("find")
        fmt = self.time_parser.get("format")
        if not find or not fmt:
            raise ValueError(
                "time_parser needs to be a dict with `find` and `format` keys"
            )

        time_string = re.search(find, line)
        if not time_string:
            raise ValueError(f"Could not find time string {find} in line {line}")

        dt = datetime.datetime.strptime(time_string.group(0), fmt)

        if dt.year == 1900:
            dt = dt.replace(year=datetime.datetime.now().year)
        return (dt - datetime.datetime(1970, 1, 1)).total_seconds()

    def process_line(self, line, data):
        """
        The data dict represents the current emit object, depending
        on your interval multiple lines may be included in the same
        emit object.

        Should return the data object

        **Arguments**

        - line (`str`): log line
        - data (`dict`): current emit dict
        """

        data = self.parse_line(line)
        if not data:
            return {}

        if self.time_parser:
            try:
                data.update(ts=self.parse_time(line))
            except ValueError as exc:
                self.log.debug(exc)
                return {}

        return data

    def process_messages(self, messages):
        """
        Process vaping messages before the are emitted

        Aggregation is handled here

        **Arguments**

        - messages (`list`): list of vaping messages

        **Returns**

        Result of self.aggregate
        """

        for message in messages:
            if message["data"] and message["data"][0] and message["data"][0].get("ts"):
                message["ts"] = message["data"][0]["ts"]
        return self.aggregate(messages)
