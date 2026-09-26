from io import BytesIO

import matplotlib.pyplot as plt


def syntax_visual_signature(syntaxes):
    """Return an immutable signature containing only visualization-relevant syntax data."""
    return tuple(
        (
            str(getattr(syntax, "sid", "")),
            getattr(syntax, "parent_sid", None),
            tuple(str(tag) for tag in (getattr(syntax, "tags", None) or [])),
            float(getattr(syntax, "score", 0.0)),
        )
        for syntax in syntaxes
    )


def get_cached_visualization(cache, name, signature, builder):
    """Reuse a rendered value while its immutable input signature is unchanged."""
    entry = cache.get(name)
    if entry is not None and entry.get("signature") == signature:
        return entry["value"]

    value = builder()
    previous_build_count = 0 if entry is None else int(entry.get("build_count", 0))
    cache[name] = {
        "signature": signature,
        "value": value,
        "build_count": previous_build_count + 1,
    }
    return value


def figure_to_png_bytes(figure):
    """Serialize a Matplotlib figure for safe Streamlit session-state reuse."""
    buffer = BytesIO()
    figure.savefig(buffer, format="png", bbox_inches="tight")
    plt.close(figure)
    return buffer.getvalue()
