from spival import spival
import json

with open('test_spival.json') as f:
    config = json.load(f)

spival(config)