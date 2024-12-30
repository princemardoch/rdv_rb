import os
import sys
from flask import render_template, request, redirect, url_for, session, flash, Blueprint

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__,), '../')))

from configs.rdv import RDV_OPTIONS
from internal_module.utils import (
    get_next_weekday,
    get_datetime_for_day_time,
    datetime_to_day_string
)
from internal_module.dbs import (
    save_reservation_data
)

index_ = Blueprint('index', __name__, template_folder='index_templates')

@index_.route('/', methods=['GET'])
def home():
    return render_template('first.html')

@index_.route('/reserve', methods=['GET'])
def reserve():
    return render_template('reservation.html', rdv_info=RDV_OPTIONS)

@index_.route('/submit_reservation', methods=['POST'])
def submit_reservation():
    consultation = request.form.get('consultation')
    day = request.form.get('day')
    time = request.form.get('time')

    if not consultation or not day or not time:
        flash('Veuillez sélectionner une consultation, une date et un horaire.')
        return redirect(url_for('index.reserve'))

    session['reservation_data'] = {
        'consultation': consultation,
        'day': day,
        'time': time,
    }

    return redirect(url_for('index.contact'))

@index_.route('/contact', methods=['GET', 'POST'])
def contact():
    if not session.get('reservation_data'):
        print("Pas de données dans la session.")
        return redirect(url_for('index.reserve'))
    if request.method == 'POST':
        reservation_data = session.get('reservation_data')
        country = request.form.get('country')
        phone = request.form.get('phone')
        fullname = request.form.get('fullname')
        experience = request.form.get('experience')
        employees = request.form.get('employees')
        revenue = request.form.get('revenue')
        expectations = request.form.get('expectations')
        
        consultation = reservation_data.get('consultation')
        day = get_next_weekday(reservation_data.get('day'))
        time = reservation_data.get('time')
        full_datetime = get_datetime_for_day_time(reservation_data.get('day'), time)
        
        save_reservation_data_response = save_reservation_data(country, phone, fullname, experience, employees, revenue, expectations, consultation, day, time, full_datetime)
        if save_reservation_data_response == 'success_write':
            session['reservation_data'] = {
                'consultation': consultation,
                'day': datetime_to_day_string(day),
                'time': time,
            }
            return redirect(url_for('index.success'))
    return render_template('form.html')

@index_.route('/success', methods=['GET'])
def success():
    reservation_data = session.get('reservation_data')
    session.clear()
    return render_template('success.html', reservation_data=reservation_data)

@index_.route('/reset', methods=['GET'])
def reset():
    session.clear()
    flash('Session réinitialisée.')
    return redirect(url_for('index'))
