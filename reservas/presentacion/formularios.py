from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    HiddenField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    TextAreaField,
    TimeField,
)
from wtforms.validators import InputRequired, Length, NumberRange, Optional, Regexp

REQUERIDO = InputRequired(message="Completa este campo.")


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


class MesaForm(FlaskForm):
    restaurante_id = SelectField("Restaurante", coerce=int, validators=[REQUERIDO])
    id = HiddenField(validators=[Optional(), Regexp(r"^\d+$")])
    numero = StringField("Número de mesa", validators=[REQUERIDO, Length(max=20)])
    capacidad = IntegerField("Capacidad", validators=[REQUERIDO, NumberRange(min=1, max=1000)])
    activa = BooleanField("Mesa disponible para nuevas reservas", default=True)


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
