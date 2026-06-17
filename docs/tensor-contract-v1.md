# Tensor Contract v1

Module: `traceleak/tensor_contract.py`

Format: `traceleak.tensor_contract.v1`

Purpose: fix the field names consumed by sequence and graph model paths.

Sequence field group:

- event_token_ids
- event_type_ids
- time_step_ids
- variable_state_ids
- attention_mask

Graph field group:

- node_feature_ids
- edge_index
- edge_type_ids
- node_time_step_ids
- graph_mask

This is a schema contract only. It does not build tensors yet.
