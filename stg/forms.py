from quart_wtf import QuartForm
from wtforms import TextAreaField, SubmitField
from quart_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired, Length


class DecodeForm(QuartForm):
    image = FileField(
        "Select Image",
        validators=[FileRequired(), FileAllowed(["jpg", "png", "jpeg"])],
    )
    submit = SubmitField("Decode")


class EncodeForm(DecodeForm):
    secret_text = TextAreaField(
        "Secret Text", validators=[DataRequired(), Length(min=1, max=1000)]
    )
    submit = SubmitField("Encode")


class EncodeFileForm(DecodeForm):
    text_file = FileField(
        "Select input file", validators=[FileRequired(), FileAllowed(["txt", "docx"])]
    )
    submit = SubmitField("Encode")
