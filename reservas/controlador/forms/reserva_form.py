"""Formulario Flask-WTF."""
from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, HiddenField, IntegerField, PasswordField, SelectField, StringField, TextAreaField, TimeField
from wtforms.validators import InputRequired, Length, NumberRange, Optional, Regexp
from reservas.controlador.validadores import REQUERIDO

class ReservaForm(FlaskForm):
    restaurante_id = SelectField("Restaurante", coerce=int, validators=[REQUERIDO])
    fecha = DateField("Fecha", validators=[REQUERIDO])
    hora = StringField(
        "Hora", validators=[REQUERIDO, Regexp(r"^\d{2}:\d{2}$", message="Selecciona una hora.")]
    )
    personas = IntegerField(
        "Personas",
        validators=[
            REQUERIDO,
            NumberRange(min=1, max=1000, message="Ingresa entre 1 y 1000 personas."),
        ],
    )
    observaciones = TextAreaField(
        "Observaciones (opcional)",
        validators=[Length(max=500, message="Escribe como máximo 500 caracteres.")],
    )
    cliente_id = SelectField("Cliente", coerce=int, validators=[Optional()])
    token_operacion = HiddenField(validators=[REQUERIDO, Length(min=20, max=128)])
