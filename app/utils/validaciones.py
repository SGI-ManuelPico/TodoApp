def validar_contraseña(v):
    if v is None:
        return v
    if not any(char.islower() for char in v):
        raise ValueError('La contraseña debe contener al menos una letra minúscula')
    if not any(char.isdigit() for char in v):
        raise ValueError('La contraseña debe contener al menos un número')
    if len(v) < 6 or len(v) > 50:
        raise ValueError('La contraseña debe tener entre 6 y 50 caracteres')
    return v