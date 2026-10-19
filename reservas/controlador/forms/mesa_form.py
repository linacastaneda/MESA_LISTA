"""Formulario Flask-WTF."""
from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, HiddenField, IntegerField, PasswordField, SelectField, StringField, TextAreaField, TimeField
from wtforms.validators import InputRequired, Length, NumberRange, Optional, Regexp
from reservas.controlador.validadores import REQUERIDO

class MesaForm(FlaskForm):
    restaurante_id = SelectField("Restaurante", coerce=int, validators=[REQUERIDO])
    id = HiddenField(validators=[Optional(), Regexp(r"^\d+$")])
    numero = StringField("Número de mesa", validators=[REQUERIDO, Length(max=20)])
    capacidad = IntegerField("Capacidad", validators=[REQUERIDO, NumberRange(min=1, max=1000)])
    activa = BooleanField("Mesa disponible para nuevas reservas", default=True)
