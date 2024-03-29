# Copyright 2011 the authors of BookTrader (see the AUTHORS file included).
#
# This file is part of BookTrader.
#
# BookTrader is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, version 3 of the License.
#
# BookTrader is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even any implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License version 3 for more details.
#
# You should have received a copy of the GNU Affero General Public
# License version 3 along with BookTrader. If not, see:
# http://www.gnu.org/licenses/

import colander
import deform

import urlparse


utf8_string = lambda: colander.String(encoding="utf-8")

class SearchSchema(colander.Schema):
    query = colander.SchemaNode(utf8_string(),
                                validator = colander.Length(min=1))
    start_index = colander.SchemaNode(colander.Integer(),
                                      missing = 0,
                                      widget = deform.widget.HiddenWidget())
    limit = colander.SchemaNode(colander.Integer(),
                                missing = 10,
                                widget = deform.widget.HiddenWidget())
    types = ['books', 'users', 'groups', 'group_books']
    type = colander.SchemaNode(
        utf8_string(),
        validator = colander.OneOf(types),
        title     = "Search type",
        widget    = deform.widget.SelectWidget(values=[(t, t.capitalize())
                                                       for t in types]))

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



def url_validator(form, value):
    url = urlparse.urlparse(value)

    if not url.netloc or not (url.scheme == 'http' or url.scheme == 'https'):
        raise colander.Invalid(form, 'Invalid url.')


class GroupSchema(colander.MappingSchema):
    types       = ['public', 'private']

    name        = colander.SchemaNode(utf8_string(),
                                      validator = colander.Length(min=5, max=400),
                                      title     = "Group name")
    description = colander.SchemaNode(utf8_string(),
                                      validator = colander.Length(max=10000),
                                      widget    = deform.widget.TextAreaWidget(),
                                      missing   = u'')
    image       = colander.SchemaNode(utf8_string(),
                                      missing   = None,
                                      validator = url_validator,
                                      title     = "Group image (URL)")
    type = colander.SchemaNode(
        utf8_string(),
        validator = colander.OneOf(types),
        title     = "Group privacy",
        widget    = deform.widget.SelectWidget(values=[(t, t.capitalize())
                                                       for t in types]))
