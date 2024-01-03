def recursive_merge(new : dict, source : dict):
    build_dict  = {}
    # Merge with source on the correct version
    for k, v in source.items():
        try:
            val     = new[k]
        except KeyError: 
            build_dict[k] = v
            continue
        if isinstance(v, dict) and v != {}: 
            build_dict[k] = recursive_merge(val, v)
        else: build_dict[k] = val
    # Add remaining fields from build_dict
    for k, v in new.items():
        try:
            val     = build_dict[k]
        except KeyError:
            build_dict[k]   = v
    return build_dict