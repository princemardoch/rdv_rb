from flask import render_template, request, redirect, url_for, session, flash, Blueprint
from configs.rdv import RDV_OPTIONS

index_ = Blueprint('index', __name__, template_folder='index_templates')

@index_.route('/', methods=['GET'])
def home():
    return render_template('first.html')

@index_.route('/reserve', methods=['GET'])
def reserve():
    print(RDV_OPTIONS)
    return render_template('reservation.html', rdv_info=RDV_OPTIONS)

@index_.route('/submit_reservation', methods=['POST'])
def submit_reservation():
    print(request.form)
    consultation = request.form.get('consultation')
    day = request.form.get('day')
    time = request.form.get('time')

    if not consultation or not day or not time:
        flash('Veuillez sélectionner une consultation, une date et un horaire.')
        return redirect(url_for('reserve'))

    session['reservation'] = {
        'consultation': consultation,
        'day': day,
        'time': time
    }

    return redirect(url_for('contact'))

@index_.route('/contact', methods=['GET'])
def contact():
    return render_template('form.html')

@index_.route('/success', methods=['GET'])
def success():
    return render_template('success.html')

@index_.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')

    if not name or not email or not phone:
        flash('Veuillez fournir votre nom, email et numéro de téléphone.')
        return redirect(url_for('contact'))

    session['contact'] = {
        'name': name,
        'email': email,
        'phone': phone
    }

    return redirect(url_for('confirmation'))

@index_.route('/confirmation', methods=['GET'])
def confirmation():
    reservation = session.get('reservation')
    contact = session.get('contact')

    if not reservation or not contact:
        flash('Il manque des informations pour la confirmation de votre réservation.')
        return redirect(url_for('reserve'))

    return render_template('confirmation.html', reservation=reservation, contact=contact)

@index_.route('/reset', methods=['GET'])
def reset():
    session.clear()
    flash('Session réinitialisée.')
    return redirect(url_for('index'))
