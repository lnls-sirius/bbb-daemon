from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from common.entity.entities import Type, Node


class EditNodeForm(FlaskForm):
    ip_address = StringField("IP Address", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    type = SelectField("Type", validators=[DataRequired()])
    sector = SelectField("Sector", validators=[DataRequired()])
    pv_prefix = StringField("PV Prefix", validators=[DataRequired()])
    submit = SubmitField("Save Changes")

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
    repo_url = StringField("Repository Url", validators=[DataRequired()])
    rc_local_path = StringField("Path to rc.local", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Save Changes")

    def set_initial_values(self, type: Type):
        if type is not None:
            self.name.data = type.name
            self.repo_url.data = type.repoUrl
            self.rc_local_path.data = type.rcLocalPath
            self.description.data = type.description
