def get_airquality_desc(score):
    '''
    Convert Air Quality Index (AQI) into descriptive text in German
    see https://aqicn.org/scale/de/
    '''
    import numpy as np
    if score == None or np.isnan(score):
        s = "Keine Daten"
    elif score < 51:
        s = "Gut"
    elif score < 101:
        s = "Mäßig"
    elif score < 151:
        s = "Ungesund für empfindliche Personengruppen"
    elif score < 201:
        s = "Ungesund"
    elif score < 301:
        s = "Sehr ungesund"
    else:
        s = "gesundheitsgefährdend"
    return s