from flask_wtf.file import FileAllowed, FileField
from wtforms import Form, IntegerField, StringField, TextAreaField, validators


class Addproducts(Form):
    name=StringField('Name', [validators.DataRequired()])
    price=IntegerField('Price', [validators.DataRequired()])
    discount=IntegerField('Discount')
    stock=IntegerField('Stock', [validators.DataRequired()])
    description=TextAreaField('Description', [validators.DataRequired()])
    colors=TextAreaField('Colors', [validators.DataRequired()])

    images = FileField('Images', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only please')
    ])
