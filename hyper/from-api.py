import csv

import spell.client
from spell.client.runs import RunsService
from spell.api.models import ValueSpec

METRIC_NAME="value"

# Create a Spell client
client = spell.client.from_environment()

# Launch a basic grid search. The first argument are the parameters
# they are a dictionary of their name mapped to the array of values
# new_grid_search accepts most run arguments as kwargs as well
#
# This launches a 6 run search
# a: 0, b: 1.3
# a: 2, b: 1.3
# a: 4, b: 1.3
# a: 0, b: 1.7
# a: 2, b: 1.7
# a: 4, b: 1.7
search = client.hyper.new_grid_search(
    {'a': ValueSpec([0,2,4]),
     'b': ValueSpec([1.3, 1.7])},
    github_url="https://github.com/spellrun/spell-examples.git",
    command="python hyperparameters/basic.py --start :a: --stepsize :b: --steps 30",
)

print("Launched a search with runs: {}".format([r.id for r in search.runs]))
print("Waiting for the runs to finish...")

# Wait for all runs to complete
for run in search.runs:
    run.wait_status(*RunsService.FINAL)
    run.refresh()
    if run.status != RunsService.COMPLETE:
        print("Warning run {} finished with status {}".format(run.id, run.status))
    elif run.user_exit_code != 0:
        print("Warning run {} finished with nonzero exit code {}".format(run.id, run.user_exit_code))

print("All runs complete")

# Collect all metrics and put in a CSV
# Metrics are all of the form (time, index, value)
# here we just extract the value and create a CSV with a row per run
rows = [['Run ID']]
for run in search.runs:
    rows.append([str(run.id)] + [str(round(v[2], 5)) for v in run.metrics(METRIC_NAME)])

with open("hyper_search_{}.csv".format(str(search.id)), "w", newline='') as csv_file:
    csv.writer(csv_file).writerows(rows)
