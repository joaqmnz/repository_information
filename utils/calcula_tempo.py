def hora(segundos: int) -> str:
    hora = segundos / 3600
    minutos = (hora % 1) * 60
    segundos = (minutos % 1) * 60
    hora = round(hora - (hora % 1))
    minutos = round(minutos - (minutos % 1))
    segundos = round(segundos - (segundos % 1))
    return f'{hora}h {minutos}min {segundos}s'
