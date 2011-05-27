import colander

utf8_string = lambda: colander.String(encoding="utf-8")

class SearchSchema(colander.Schema):
    query = colander.SchemaNode(utf8_string())

