import colander

utf8_string = lambda: colander.String(encoding="utf-8")

class SearchSchema(colander.Schema):
    query = colander.SchemaNode(utf8_string(),
                                validator=colander.Length(min=1))



class AuthorsSchema(colander.SequenceSchema):
    author = colander.SchemaNode(utf8_string())

class IndustryIdentifierSchema(colander.MappingSchema):
    type       = colander.SchemaNode(utf8_string(), name = "type")
    identifier = colander.SchemaNode(utf8_string())

class IndustryIdentifiersSchema(colander.SequenceSchema):
    identifier = IndustryIdentifierSchema()

class VolumeInfoSchema(colander.MappingSchema):
    title       = colander.SchemaNode(utf8_string())
    subtitle    = colander.SchemaNode(utf8_string(), missing="")
    authors     = AuthorsSchema(missing=[])
    publisher   = colander.SchemaNode(utf8_string(), missing="")
    industryIdentifiers = IndustryIdentifiersSchema()
    description = colander.SchemaNode(utf8_string(), missing="")
    publishedDate = colander.SchemaNode(utf8_string(), missing="")

class BookSchema(colander.MappingSchema):
    id         = colander.SchemaNode(utf8_string())
    volumeInfo = VolumeInfoSchema()
