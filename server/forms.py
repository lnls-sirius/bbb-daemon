from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField, FieldList
from wtforms.validators import DataRequired, Regexp

from common.entity.entities import Node, Type


class EditNodeForm(FlaskForm):
    ip_address = StringField("IP Address", validators=[DataRequired(), Regexp('^([0-9]{1,3}\.){3}[0-9]{1,3}$',
                                                                              message='Must be a valid ip! xxx.xxx.xxx.xxx')])
    name = StringField("Name", validators=[DataRequired(), Regexp('[^\s]', message='Spaces are not allowed!')])
    type = SelectField("Type", validators=[DataRequired()])
    sector = SelectField("Sector", validators=[DataRequired()])
    submit = SubmitField("Save Changes")

    pv_prefix = TextAreaField("PV Prefix", validators=[DataRequired()])

    def set_initial_values(self, node: Node):
        if node is not None:
            self.ip_address.data = node.ipAddress
            self.name.data = node.name

            if node.type is None:
                self.type.data = ''
            else:
                self.type.data = node.type.name

            self.sector.data = node.sector
            self.pv_prefix.data = node.pvPrefix


class EditTypeForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    repo_url = StringField("Repository Url", validators=[DataRequired()], id='repo_url')
    rc_local_path = StringField("Path to rc.local", validators=[DataRequired()], id='rc_local_path')
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Save Changes")

    def set_initial_values(self, type: Type):
        if type is not None:
            self.name.data = type.name
            self.repo_url.data = type.repoUrl
            self.rc_local_path.data = type.rcLocalPath
            self.description.data = type.description
