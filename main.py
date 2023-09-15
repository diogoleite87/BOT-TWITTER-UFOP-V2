from api import client
from datetime import date
import json

def is_within_validity_period(current_date, validity_from, validity_to):
    validity_from = date.fromisoformat(validity_from)
    validity_to = date.fromisoformat(validity_to)

    return validity_from <= current_date <= validity_to

def day_counter(current_date, date_to):
    date_to = date.fromisoformat(date_to)

    time_difference = date_to - current_date

    days_remaining = time_difference.days

    return days_remaining + 1

def post_message(message):
    client.create_tweet(message)

def verify_date_post(commemorative_date, period, current_date):
    days_remaining = day_counter(current_date, commemorative_date['date'])

    if days_remaining == 0:
        message = f"ATENÇÃO: Hoje é {commemorative_date['message']} do período {period}."
        post_message(message)
    elif days_remaining > 0:
        message = f"Faltam {days_remaining} dias para {commemorative_date['message']} do perído {period}."
        if days_remaining == 1:
            message = f"Falta {days_remaining} dia para {commemorative_date['message']} do perído {period}."
            post_message(message)
        elif days_remaining <= 7:
            post_message(message)
        elif days_remaining <= 30 and days_remaining % 2 == 0:
            post_message(message)
        elif days_remaining <= 60 and days_remaining % 3 == 0:
            post_message(message)
        else:
            if days_remaining % 5 == 0:
                post_message(message)


def verify_dates_in_period(commemorative_dates, period, current_date):
    for commemorative_date in commemorative_dates:
        if is_within_validity_period(current_date, commemorative_date['validity_from'], commemorative_date['validity_to']):
            verify_date_post(commemorative_date, period, current_date)
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
                verify_dates_in_period(period['commemorative_dates'], period['period'], current_date)
            else:
                print(f"The current date {current_date} is outside the validity for period {period['period']}.")