from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField

# Account form to utilize profile picture feature - file field allows users to selct and submit an image file
 
class UpdateAccountForm(FlaskForm):
    
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

