# ◆genealogy_plot.py（構文系譜）旧genealogy.py
import networkx as nx
import matplotlib.pyplot as plt

def draw_syntax_genealogy(syntaxes, use_streamlit=False, figsize=(6, 4)):
    G = nx.DiGraph()

    for syn in syntaxes:
        sid = syn.sid[:8]
        G.add_node(sid, label=sid)

        if syn.parent_sid:
            parents = syn.parent_sid.split("&")
            for p in parents:
                G.add_edge(p[:8], sid)

    pos = nx.spring_layout(G, seed=42)
    fig = plt.figure(figsize=figsize)
    nx.draw(G, pos, with_labels=True, node_color='lightgreen', node_size=1000, font_size=10)
    plt.title("構文進化系譜 (SID Genealogy)")

    if use_streamlit:
        import streamlit as st
        st.pyplot(fig)
    else:
        plt.show()
