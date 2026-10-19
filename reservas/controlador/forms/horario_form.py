"""Formulario Flask-WTF."""
from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, HiddenField, IntegerField, PasswordField, SelectField, StringField, TextAreaField, TimeField
from wtforms.validators import InputRequired, Length, NumberRange, Optional, Regexp
from reservas.controlador.validadores import REQUERIDO

class HorarioForm(FlaskForm):
    restaurante_id = SelectField("Restaurante", coerce=int, validators=[REQUERIDO])
    id = HiddenField(validators=[Optional(), Regexp(r"^\d+$")])
    dia_semana = SelectField(
        "Día de la semana",
        coerce=int,
        validators=[REQUERIDO],
        choices=[
            (1, "Lunes"),
            (2, "Martes"),
            (3, "Miércoles"),
            (4, "Jueves"),
            (5, "Viernes"),
            (6, "Sábado"),
            (7, "Domingo"),
        ],
    )
    apertura = TimeField("Apertura", validators=[REQUERIDO])
    cierre = TimeField("Cierre", validators=[REQUERIDO])
