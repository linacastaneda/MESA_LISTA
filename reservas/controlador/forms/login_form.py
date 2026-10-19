"""Formulario Flask-WTF."""
from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, HiddenField, IntegerField, PasswordField, SelectField, StringField, TextAreaField, TimeField
from wtforms.validators import InputRequired, Length, NumberRange, Optional, Regexp
from reservas.controlador.validadores import REQUERIDO

class LoginForm(FlaskForm):
    correo = StringField(
        "Correo electrónico",
        validators=[
            REQUERIDO,
            Length(max=254),
            Regexp(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", message="Escribe un correo válido."),
        ],
    )
    clave = PasswordField("Contraseña", validators=[REQUERIDO, Length(max=256)])
