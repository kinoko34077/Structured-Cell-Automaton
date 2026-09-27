def syntax_signature(syntaxes, include_score=True):
    """Build a stable UI signature with only the fields a renderer consumes."""
    return tuple(
        (
            syn.sid,
            getattr(syn, "parent_sid", None),
            tuple(syn.tags),
            syn.score if include_score else None,
        )
        for syn in syntaxes
    )


def get_cached_figure(cache, key, signature, builder):
    """Return a cached figure, rebuilding it only when its input signature changes."""
    entry = cache.get(key)
    if entry is not None and entry["signature"] == signature:
        return entry["figure"]

    figure = builder()
    cache[key] = {"signature": signature, "figure": figure}
    return figure
