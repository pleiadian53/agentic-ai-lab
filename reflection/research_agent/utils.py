from IPython.display import display, HTML

def show_output(title, content, background="#f0f0f0", text_color="#000000"):
    html = f"""
    <div style="
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: {background};
        color: {text_color};
    ">
        <h3 style="margin-top: 0;">{title}</h3>
        <pre style="
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 14px;
        ">{content}</pre>
    </div>
    """
    display(HTML(html))
