from api import client_v1, client_v2
from datetime import date
import json
from PIL import Image, ImageDraw


def is_within_validity_period(current_date, validity_from, validity_to):
    validity_from = date.fromisoformat(validity_from)
    validity_to = date.fromisoformat(validity_to)

    return validity_from <= current_date <= validity_to


def day_counter(current_date, date_to):
    date_to = date.fromisoformat(date_to)

    time_difference = date_to - current_date

    days_remaining = time_difference.days

    return days_remaining


def create_progress_bar(total_days, days_remaining, filename):
    progress_percentage = (total_days - days_remaining) / total_days * 100

    width = 250
    height = 50
    image = Image.new('RGB', (width, height), color='white')

    draw = ImageDraw.Draw(image)

    border_color = 'black'
    border_thickness = 1
    draw.rectangle([(10 - border_thickness, 10 - border_thickness),
                    (width - 10 + border_thickness, height - 10 + border_thickness)],
                   outline=border_color, width=border_thickness)

    bar_width = int((width - 20) * progress_percentage / 100)
    draw.rectangle([(10, 10), (10 + bar_width, height - 10)], fill='#8B0000')

    image.save(filename)


def post_message(message, total_days, days_remaining, progress_bar, warning_message):

    if progress_bar:

        progress_percentage = round((total_days - days_remaining) / total_days * 100, 1)

        if warning_message:
            final_message = f'{message}\n\n{warning_message}\n\n{progress_percentage}% {progress_bar["message"]}'
        else:
            final_message = f'{message}\n\n{progress_percentage}% {progress_bar["message"]}'

        create_progress_bar(total_days, days_remaining, 'progress_bar.png')

        media = client_v1.media_upload(filename='progress_bar.png')

        client_v2.create_tweet(text=final_message, media_ids=[media.media_id])

    else:
        if warning_message:
            final_message = f'{message}\n\n{warning_message}'
        else:
            final_message = message
        client_v2.create_tweet(text=message)


def verify_date_post(commemorative_date, period, current_date, warning_message):
    days_remaining = day_counter(current_date, commemorative_date['date'])
    total_days = day_counter(date.fromisoformat(
        commemorative_date['validity_from']), commemorative_date['validity_to'])

    if days_remaining == 0:
        message = f"ATENÇÃO: Hoje é {commemorative_date['message']} do período {period}."
        post_message(message, total_days, days_remaining,
                     commemorative_date['progress_bar'], warning_message)
    elif days_remaining > 0:
        message = f"Faltam {days_remaining} dias para {commemorative_date['message']} do perído {period}."
        if days_remaining == 1:
            message = f"Falta {days_remaining} dia para {commemorative_date['message']} do perído {period}."
            post_message(message, total_days, days_remaining,
                         commemorative_date['progress_bar'], warning_message)
        elif days_remaining <= 7:
            post_message(message, total_days, days_remaining,
                         commemorative_date['progress_bar'], warning_message)
        elif days_remaining <= 30 and days_remaining % 2 == 0:
            post_message(message, total_days, days_remaining,
                         commemorative_date['progress_bar'], warning_message)
        elif days_remaining <= 60 and days_remaining % 3 == 0:
            post_message(message, total_days, days_remaining,
                         commemorative_date['progress_bar'], warning_message)
        else:
            if days_remaining % 5 == 0:
                post_message(message, total_days, days_remaining,
                             commemorative_date['progress_bar'], warning_message)


def verify_dates_in_period(commemorative_dates, period, current_date, warning_message):
    for commemorative_date in commemorative_dates:
        if is_within_validity_period(current_date, commemorative_date['validity_from'], commemorative_date['validity_to']):
            verify_date_post(commemorative_date, period, current_date, warning_message)
        else:
            print(f"The current date {current_date} is outside the validity "
                  f"({commemorative_date['validity_from']} - {commemorative_date['validity_to']}) "
                  f"for commemorative date {commemorative_date['message']} in period {period}.")


if __name__ == '__main__':

    current_date = date.today()

    with open('./data.json', 'r', encoding='utf-8') as json_file:
        dates = json.load(json_file)

        for period in dates:
            if is_within_validity_period(current_date, period['validity_from'], period['validity_to']):
                verify_dates_in_period(
                    period['commemorative_dates'], period['period'], current_date, period['warning_message'])
            else:
                print(
                    f"The current date {current_date} is outside the validity for period {period['period']}.")
