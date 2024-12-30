import sys
import os
from datetime import datetime, timedelta
from functools import wraps
from threading import Lock
import time
import hashlib
import random

from flask import render_template, request, redirect, url_for, session, flash, Blueprint

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__,), '../')))

from internal_module.dbs import (
    get_all_reservations,
    update_reservation,
    get_reservation_by_id,
    get_dashboard_stats,
    get_reservations_by_date,
    delete_reservation_by_id
)

admin = Blueprint('admin', __name__, template_folder='admin_templates')

@admin.before_request
def require_login():
    public_routes = ['admin.login']
    
    if 'admin_logged_in' not in session and request.endpoint not in public_routes:
        flash('Veuillez vous connecter pour accéder à cette page', 'error')
        return redirect(url_for('admin.login'))

# Gestionnaire de tentatives de connexion thread-safe
class LoginAttemptManager:
    def __init__(self, max_attempts=5, lockout_duration=300):  # 300 secondes = 5 minutes
        self._attempts = {}  # Stocke les tentatives par IP + user agent
        self._lockouts = {}  # Stocke les verrouillages
        self._lock = Lock()  # Pour thread-safety
        self.max_attempts = max_attempts
        self.lockout_duration = lockout_duration

    def _get_identifier(self, request):
        """
        Crée un identifiant unique basé sur l'IP et le User-Agent
        Utilise également X-Forwarded-For pour gérer les cas derrière un proxy
        """
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')
        # Créer un hash unique de l'IP et du User-Agent
        identifier = hashlib.sha256(f"{ip}:{user_agent}".encode()).hexdigest()
        return identifier

    def _cleanup_old_attempts(self):
        """Nettoie les anciennes tentatives pour éviter les fuites de mémoire"""
        current_time = time.time()
        with self._lock:
            # Nettoyer les tentatives expirées
            self._attempts = {
                k: v for k, v in self._attempts.items()
                if current_time - v[-1] < self.lockout_duration
            }
            # Nettoyer les verrouillages expirés
            self._lockouts = {
                k: v for k, v in self._lockouts.items()
                if current_time < v
            }

    def is_locked_out(self, request):
        """Vérifie si l'identifiant est verrouillé"""
        identifier = self._get_identifier(request)
        current_time = time.time()
        
        with self._lock:
            # Vérifier si l'identifiant est verrouillé
            if identifier in self._lockouts:
                lockout_end = self._lockouts[identifier]
                if current_time < lockout_end:
                    # Calculer le temps restant
                    remaining = int(lockout_end - current_time)
                    return True, remaining
                else:
                    # Le verrouillage est expiré, on le supprime
                    del self._lockouts[identifier]
                    if identifier in self._attempts:
                        del self._attempts[identifier]
        
        return False, 0

    def record_attempt(self, request, success):
        """Enregistre une tentative de connexion"""
        identifier = self._get_identifier(request)
        current_time = time.time()
        
        with self._lock:
            if success:
                # En cas de succès, on réinitialise les tentatives
                if identifier in self._attempts:
                    del self._attempts[identifier]
                if identifier in self._lockouts:
                    del self._lockouts[identifier]
                return True

            # En cas d'échec
            if identifier not in self._attempts:
                self._attempts[identifier] = []
            
            self._attempts[identifier].append(current_time)
            
            # Ne garder que les dernières tentatives dans la fenêtre de temps
            self._attempts[identifier] = [
                t for t in self._attempts[identifier]
                if current_time - t < self.lockout_duration
            ]
            
            # Vérifier si on doit verrouiller
            if len(self._attempts[identifier]) >= self.max_attempts:
                self._lockouts[identifier] = current_time + self.lockout_duration
                return False

        # Nettoyer périodiquement
        if random.random() < 0.1:  # 10% de chance de nettoyage à chaque tentative
            self._cleanup_old_attempts()
            
        return True

# Créer une instance globale du gestionnaire
login_manager = LoginAttemptManager()

def check_login_attempts(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Vérifier si l'utilisateur est verrouillé
        is_locked, remaining_time = login_manager.is_locked_out(request)
        
        if is_locked:
            flash(f'Trop de tentatives de connexion. Veuillez attendre {remaining_time} secondes.', 'error')
            return render_template('login.html')
            
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/login', methods=['GET', 'POST'])
@check_login_attempts
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email == "rogerbango10@gmail.com" and password == "201200@Rr":
            login_manager.record_attempt(request, success=True)
            session['admin_logged_in'] = True
            session['email'] = email
            flash('Connexion réussie', 'success')
            return redirect(url_for('admin.home'))
        else:
            login_manager.record_attempt(request, success=False)
            flash('Identifiants incorrects', 'error')
    
    return render_template('login.html')

@admin.route('/')
def home():
    return redirect(url_for('admin.reservations'))

@admin.route('/reservations')
def reservations():
    reservations_data = get_all_reservations()
    stats = get_dashboard_stats()
    if reservations_data is None:
        return "Une erreur est survenue"
    
    return render_template('dashboard.html', reservations=reservations_data, stats=stats)

@admin.route('/edit/<int:rdv_id>', methods=['GET', 'POST'])
def edit_reservation(rdv_id):
    if request.method == 'POST':
        data = {
            'id': rdv_id,
            'phone_number': request.form.get('phone_number'),
            'fullname': request.form.get('fullname'),
            'day': request.form.get('day'),
            'time': str(request.form.get('time')),
            'status': request.form.get('status'),
            'notes': request.form.get('notes')
        }

        if update_reservation(rdv_id, data):
            flash('Modification effectuée avec succès', 'success')
            return redirect(url_for('admin.home'))
        flash('Une erreur est survenue', 'error')
        return redirect(url_for('admin.home'))
    else:
        reservation = get_reservation_by_id(rdv_id)
        if reservation:
            return render_template('edit.html', reservation=reservation)
        return redirect(url_for('admin.home'))

@admin.route('/calendar')
def calendar():
    reservations = get_reservations_by_date()

    today = datetime.today()
    tomorrow = today + timedelta(days=1)
    after_tomorrow = today + timedelta(days=2)

    return render_template('calendar.html', 
                           reservations=reservations,
                           today=datetime.today(),
                           tomorrow=tomorrow,
                           after_tomorrow=after_tomorrow)

@admin.route('/delete/<int:rdv_id>', methods=['POST'])
def delete_reservation(rdv_id):
    if delete_reservation_by_id(rdv_id):
        flash('Rendez-vous supprimé avec succès', 'success')
    else:
        flash('Une erreur est survenue ou le rendez-vous n’existe pas', 'error')

    return redirect(url_for('admin.reservations'))
