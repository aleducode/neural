"""General Utilities."""


def generate_calendar_google_invite(name_user, date, init_hour, end_hour):
    date = date.strftime("%Y%m%d")
    init = init_hour.strftime("%H%M")
    end = end_hour.strftime("%H%M")
    return "https://calendar.google.com/calendar/u/0/r/eventedit?text=Neural+Entrenamiento+{username}&dates={date}T{init}/{date}T{end}&details=Para+mas+info,+click+aqui:+http://neural.com.co&location=Innocence+Cloth,+Calle+25B+Sur,+Envigado,+Antioquia&sf=true&output=xml".format(
        username=name_user,
        date=date,
        init=init,
        end=end
    )
