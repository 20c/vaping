import os

import confu.config
import confu.schema
import pytest
import yaml

import vaping.schema


def test_quickstart_schema(schema_dir):
    config_path = os.path.join(schema_dir, "quickstart.yml")
    with open(config_path, 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            pytest.fail()


    schema = vaping.schema.VapingSchema()

    success, errors, warnings = confu.schema.validate(schema, data)

    config = confu.config.Config(schema, data)
    pprint(config.__dict__)
    
