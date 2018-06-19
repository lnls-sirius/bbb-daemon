from marshmallow import Schema, fields


class TypeSchema(Schema):
    name = fields.Str()
    color = fields.List(fields.Str())
    repoUrl = fields.Str()
    description = fields.Str()
    sha = fields.Str()


class NodeSchema(Schema):
    name = fields.Str()
    ipAddress = fields.Str()
    state_string = fields.Str()
    misconfiguredColor = fields.Str()
    pvPrefix = fields.List(fields.Str())

    sector = fields.Field()

    state = fields.Int()
    counter = fields.Int()

    rcLocalPath = fields.Str()

    type = fields.Nested(TypeSchema())
