import colander
import deform


utf8_string = lambda: colander.String(encoding="utf-8")

class SearchSchema(colander.Schema):
    query = colander.SchemaNode(utf8_string(),
                                validator = colander.Length(min=1))
    start_index = colander.SchemaNode(colander.Integer(),
                                      missing = 0,
                                      widget = deform.widget.HiddenWidget())

class AuthorsSchema(colander.SequenceSchema):
    author = colander.SchemaNode(utf8_string())

class IndustryIdentifierSchema(colander.MappingSchema):
    type       = colander.SchemaNode(utf8_string(), name = "type")
    identifier = colander.SchemaNode(utf8_string())

class IndustryIdentifiersSchema(colander.SequenceSchema):
    identifier = IndustryIdentifierSchema()

class ImageLinkSchema(colander.MappingSchema):
    linkType  = colander.SchemaNode(utf8_string())
    link      = colander.SchemaNode(utf8_string())

class ImageLinksSchema(colander.MappingSchema):
    smallThumbnail = colander.SchemaNode(utf8_string(),
                                         name    = "smallThumbnail",
                                         missing = None)
    thumbnail      = colander.SchemaNode(utf8_string(),
                                         name    = "thumbnail",
                                         missing = None)
    small          = colander.SchemaNode(utf8_string(),
                                         name    = "small",
                                         missing = None)
    medium         = colander.SchemaNode(utf8_string(),
                                         name    = "medium",
                                         missing = None)
    large          = colander.SchemaNode(utf8_string(),
                                         name    = "large",
                                         missing = None)
    extraLarge     = colander.SchemaNode(utf8_string(),
                                         name    = "extraLarge",
                                         missing = None)

class VolumeInfoSchema(colander.MappingSchema):
    title       = colander.SchemaNode(utf8_string())
    subtitle    = colander.SchemaNode(utf8_string(), missing="")
    authors     = AuthorsSchema(missing=[])
    publisher   = colander.SchemaNode(utf8_string(), missing="")
    industryIdentifiers = IndustryIdentifiersSchema(missing=[])
    description = colander.SchemaNode(utf8_string(), missing="")
    publishedDate = colander.SchemaNode(utf8_string(), missing="")
    imageLinks  = ImageLinksSchema(missing=None)

class BookSchema(colander.MappingSchema):
    id         = colander.SchemaNode(utf8_string())
    volumeInfo = VolumeInfoSchema()



class GroupSchema(colander.MappingSchema):
    types       = ['public', 'private']

    name        = colander.SchemaNode(utf8_string(),
                                      validator = colander.Length(min=5, max=400),
                                      title     = "Group name")
    description = colander.SchemaNode(utf8_string(),
                                      validator = colander.Length(max=10000),
                                      widget    = deform.widget.TextAreaWidget(),
                                      missing   = u'')
    type = colander.SchemaNode(
        utf8_string(),
        validator = colander.OneOf(types),
        title     = "Group privacy",
        widget    = deform.widget.SelectWidget(values=[(t, t.capitalize())
                                                       for t in types]))
