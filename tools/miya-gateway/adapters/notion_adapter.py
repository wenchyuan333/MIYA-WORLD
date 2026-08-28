import os
from notion_client import Client
from tools.miya_gateway.registry import register

NOTION_TOKEN = os.getenv("NOTION_TOKEN")

client = Client(auth=NOTION_TOKEN) if NOTION_TOKEN else None

@register(name="notion.dump_page", description="Dump a Notion page's plain text")
def dump_page(page_id: str):
    if client is None:
        raise RuntimeError("NOTION_TOKEN not set")
    page = client.pages.retrieve(page_id)
    # Very simple: return title and id. Extend block parsing separately.
    title_prop = page.get("properties", {}).get("title")
    title_text = None
    if isinstance(title_prop, dict):
        title = title_prop.get("title", [])
        if title:
            title_text = "".join([t.get("plain_text", "") for t in title])
    if not title_text:
        title_text = str(page_id)
    return {"id": page_id, "title": title_text}
