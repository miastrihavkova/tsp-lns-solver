# Exact time, first thing to do
import time
PROGRAM_START_TIME = time.time()

import sys
import json

from lns import lns_solver


def _read_instance_json(file_path):
    with open(file_path) as f:
        return json.load(f)



def main():
    # Arg parse
    instance_path = sys.argv[1]
    output_path = sys.argv[2]

    # Perform LNS
    instance = _read_instance_json(instance_path)
    lns_solver(instance, PROGRAM_START_TIME, output_path)

# Run
main()
