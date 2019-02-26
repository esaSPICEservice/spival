from spival import write_BepiColombo
import json

with open('test_bepic.json') as f:
    config = json.load(f)

write_BepiColombo(config)