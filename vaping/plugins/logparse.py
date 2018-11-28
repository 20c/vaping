from __future__ import absolute_import

import logging
import re

import vaping

@vaping.plugin.register("logparse")
class LogParse(vaping.plugins.FileProbe):
    """
    Log parse plugin base

    Will parse a log line by line and probe to emit data
    over a specified interval.

    config:
        `interval` probe/emit interval
        `path` log file path
    """

    default_config = {
        'parser' : '(\S+)=(\S+)',
        'fields' : {},
        'exclude' : [],
        'include' : [],
        'aggregate' : {}
    }

    def init(self):
        self.stack = []
        self.fields = self.config.get("fields")
        self.aggregate_count = self.config.get("aggregate").get("count", 0)
        self.exclude = self.config.get("exclude", [])
        self.include = self.config.get("include", [])

    def parse_line(self, line):
        """
        Here is where we parse values out of a single line read from the log
        and return a dict containg keys and values
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

        fields = self.config.get("fields",{})

        data = {}

        for k,v in fields.items():
            data[k] = self.parse_field_value(v, line)

        for k,v in fields.items():
            if "eval" in v:
                data[k] = eval(v["eval"].format(**data))
            if "type" in v:
                data[k] = __builtins__.get(v["type"]).__call__(data[k])

            print(k, data[k])

        return data


    def parse_field_value(self, field, line):
        value = None
        if "parser" in field:
            match = re.search(field["parser"], line)
            if not match:
                raise ValueError("Could not parse field value {}\n{}".format(field, line))
            value = match.group(1)

        if "type" in field and value is not None:
            value = __builtins__.get(field["type"]).__call__(value)

        return value


    def aggregate(self, messages):

        if not self.aggregate_count:
            return messages

        rv = []

        self.stack = self.stack + messages


        if len(self.stack) < self.aggregate_count:
            return rv


        while len(self.stack) >= self.aggregate_count:
            message = self.stack[0]

            self.stack.remove(self.stack[0])
            for other in self.stack[:self.aggregate_count-1]:
                message["data"].extend(other["data"])
                self.stack.remove(self.stack[0])
            rv.append(message)

        for message in rv:
            self.aggregate_message(message)

        return rv


    def aggregate_message(self, message):
        main = message["data"][0]
        finalizers = ["eval"]

        for k,v in self.fields.items():
            if v.get("aggregate") not in finalizers:
                main[k] = self.aggregate_field(k, message["data"])

        for k,v in self.fields.items():
            if v.get("aggregate") in finalizers:
                main[k] = self.aggregate_field(k, message["data"])

        main["messages"] = len(message["data"])
        message["data"] = [main]


    def aggregate_field(self, field_name, rows):
        field = self.fields.get(field_name,{})
        if "aggregate" not in field:
            return rows[-1][field_name]

        aggregate = getattr(self,
            "aggregate_{}".format(field.get("aggregate")))
        r = aggregate(field_name, rows)
        print(field_name, r, "aggregated")
        return r


    def aggregate_sum(self, field_name, rows):
        c = 0
        for row in rows:
            c = c + row.get(field_name, 0)
        return c

    def aggregate_eval(self, field_name, rows):
        return eval(self.fields[field_name].get("eval").format(
            **rows[0]))


    def aggregate_avg(self, field_name, rows):
        return self.aggregate_sum(field_name, rows) / len(rows)



    def process_line(self, line, data):
        """
        The data dict represents the current emit object, depending
        on your interval multiple lines may be included in the same
        emit object.

        Should return the data object
        """

        data.update(self.parse_line(line))
        return data


    def process_messages(self, messages):
        return self.aggregate(messages)

