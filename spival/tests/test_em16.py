from spival import write_ExoMars2016
import json

with open('test_em16.json') as f:
    config = json.load(f)

write_ExoMars2016(config)