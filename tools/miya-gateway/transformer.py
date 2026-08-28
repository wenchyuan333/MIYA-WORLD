# transformer helpers (lightweight)

def extract_title_from_properties(props: dict):
    # Try to find a title property
    for k,v in props.items():
        if isinstance(v, dict) and v.get('type') == 'title':
            return ''.join([t.get('plain_text','') for t in v.get('title',[])])
    # fallback to name-like properties
    for k,v in props.items():
        if isinstance(v, dict) and v.get('type') in ('rich_text','rich_texts','text'):
            arr = v.get(v.get('type'), [])
            if arr:
                return ''.join([t.get('plain_text','') for t in arr])
    return None
