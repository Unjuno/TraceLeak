# View Contract v1

Module: `traceleak/view_contract.py`

Format: `traceleak.view_contract.v1`

The contract describes controlled changes to model input views for local model-analysis experiments.

Required field count: 7

Supported view groups:

- token
- event
- variable
- graph_node
- graph_edge
- time_step

Supported actions:

- drop
- zero
- replace_with_bucket
- keep_only

This is a schema-level contract. It does not run a model.
