from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class EditNodeForm(FlaskForm):
    ip_address = StringField("IP Address", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    type = SelectField("Type")
    sector = StringField("Sector", validators=[DataRequired()])
    pv_prefix = StringField("PV Prefix", validators=[DataRequired()])
    submit = SubmitField("Save Changes")


class EditTypeForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    repo_url = StringField("Repository Url", validators=[DataRequired()])
    rc_local_path = StringField("Path to rc.local", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Save Changes")


'''
class UserDetails(Form):
    group_id = SelectField(u'Group', coerce=int)

def edit_user(request, id):
    user = User.query.get(id)
    form = UserDetails(request.POST, obj=user)
    form.group_id.choices = [(g.id, g.name) for g in Group.query.order_by('name')]
'''
