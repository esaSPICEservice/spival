from spival import write_MarsExpress
import json

with open('test_mex.json') as f:
    config = json.load(f)

write_MarsExpress(config)