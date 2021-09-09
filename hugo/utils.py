def format_http_date(date):
    return date.strftime("%a, %d %b %Y %H:%M:%S GMT")


def escape(string: str) -> str:
    return (
        string.replace("&", "&amp;")
        .replace(">", "&gt;")
        .replace("<", "&lt;")
        .replace("'", "&#39;")
        .replace('"', "&#34;")
    )
