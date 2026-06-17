# Model Output Contract v1

Module: `traceleak/model_output_contract.py`

Format: `traceleak.model_output.v1`

Fields:

- sample_id
- model_id
- consumer_mode
- prediction
- confidence
- metadata

Purpose: represent a schema-level model result so later evidence-chain records can connect a dataset sample, a model result, and explanation records.
