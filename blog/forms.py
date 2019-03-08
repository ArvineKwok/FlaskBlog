from wtforms import StringField, SubmitField, TextAreaField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Email

class CommentForm(FlaskForm):
    author = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 254)])
    body = TextAreaField('Comment', validators=[DataRequired])
    submit = SubmitField()