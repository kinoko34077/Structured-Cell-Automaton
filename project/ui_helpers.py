def get_cached_figure(cache, key, signature, builder):
    """Return a cached figure, rebuilding it only when its input signature changes."""
    entry = cache.get(key)
    if entry is not None and entry["signature"] == signature:
        return entry["figure"]

    figure = builder()
    cache[key] = {"signature": signature, "figure": figure}
    return figure
