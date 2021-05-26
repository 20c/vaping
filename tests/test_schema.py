import os

import confu.config
import confu.schema
import pytest
import yaml

import vaping.config
from pprint import pprint


def test_validate_quickstart_schema(schema_dir):
    config_path = os.path.join(schema_dir, "quickstart.yml")
    with open(config_path, "r") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            pytest.fail()

    schema = vaping.config.VapingSchema()

    success, errors, warnings = confu.schema.validate(schema, data)

    # In case of failure
    print([e for e in errors])
    print([w for w in warnings])
    assert success
    assert len(warnings) == 0
