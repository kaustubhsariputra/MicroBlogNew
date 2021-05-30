from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, length, EqualTo, Email, ValidationError
from MicroBlog.models import User
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed


class Signup(FlaskForm):
    fname = StringField(' First Name:', validators = [DataRequired(message='* This Field is required!!')])
    lname = StringField(' Last Name:', validators=[DataRequired(message='* This Field is required!!')])
    email = StringField(' Email ID:', validators=[DataRequired(message='* This Field is required!!'),
                                                  Email()])
    password = PasswordField(' Enter Password: ', validators =[DataRequired(message='* This Field is required!!'),
                                                               length(min=8, max=25)])
    cnfpass = PasswordField(' Enter Password Again: ', validators =[DataRequired(message='* This Field is required!!'),
                                                              length(min=8, max=25), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by (email = email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose another one!!')

class Login(FlaskForm):

    email = StringField(' Email ID:', validators=[DataRequired(message='* This Field is required!!'),
                                                  Email()])
    password = PasswordField(' Enter Password: ', validators =[DataRequired(message='* This Field is required!!'),
                                                               length(min=8, max=25)])
    remember = BooleanField('Remember Me!!')

    submit = SubmitField('Login')


class Up_date(FlaskForm):
    fname = StringField(' First Name:', validators=[DataRequired(message='* This Field is required!!')])
    lname = StringField(' Last Name:', validators=[DataRequired(message='* This Field is required!!')])
    email = StringField(' Email ID:', validators=[DataRequired(message='* This Field is required!!'),
                                                  Email()])
    picture = FileField('Upload profile picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by (email =email.data).first()
            if user:
                raise ValidationError('That email is already registered. Please choose another one!!')

    def validate_first_name(self, first_name):
        if first_name.data != current_user.first_name:
            user = User.query.filter_by (first_name =first_name.data).first()
            if user:
                raise ValidationError('That email is already registered. Please choose another one!!')

    def validate_last_name(self, last_name):
        if last_name.data != current_user.last_name:
            user = User.query.filter_by (last_name =last_name.data).first()
            if user:
                raise ValidationError('That email is already registered. Please choose another one!!')


class PostForm(FlaskForm):
    title = StringField(' Title', validators=[DataRequired(message='* This Field is required!!')])
    content = TextAreaField(' Content', validators=[DataRequired(message='* This Field is required!!')])
    submit = SubmitField('Post')


class RequestResetForm(FlaskForm):
    email = StringField(' Email ID:', validators=[DataRequired(message='* This Field is required!!'),
                                                  Email()])
    submit = SubmitField('Request password reset')
    def validate_email(self, email):
        user = User.query.filter_by (email = email.data).first()
        if user is None:
            raise ValidationError('Email does not exist!!. Create new account')

class ResetPasswordForm(FlaskForm):
    password = PasswordField(' Enter Password: ', validators=[DataRequired(message='* This Field is required!!'),
                                                              length(min=8, max=25)])
    cnfpass = PasswordField(' Enter Password Again: ', validators=[DataRequired(message='* This Field is required!!'),
                                                                   length(min=8, max=25), EqualTo('password')])
    submit = SubmitField('Reset Password')