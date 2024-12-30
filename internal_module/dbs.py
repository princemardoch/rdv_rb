import os
import sys
import sqlite3
import logging
import json
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__,), '../')))

from configs.config import Config_
rdv_db_path = Config_.DBs.rdv_db

def save_reservation_data(country: str, phone: str, fullname :str, experience :str, employees :str, revenue :str, expectations : str, consultation :str, day : datetime, time : datetime, reservation_datetime):
    try:
        with sqlite3.connect(rdv_db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            INSERT INTO reservation_data (country, phone, fullname, experience, employees, revenue, expectations, consultation, day, time, reservation_datetime, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (country, phone, fullname, experience, employees, revenue, expectations, consultation, day, time, reservation_datetime, 'pending'))
        return 'success_write'
    except Exception as e:
        logging.critical(f"Probème d'execution {e}", exc_info=True)
        return None

def get_reservations_by_date():
    try:
        with sqlite3.connect(rdv_db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT id, fullname, time, status, day FROM reservation_data WHERE status = "confirmed" ORDER BY day, time DESC LIMIT 100')
            reservations = cursor.fetchall()

            today = datetime.date.today()
            tomorrow = today + datetime.timedelta(days=1)
            after_tomorrow = today + datetime.timedelta(days=2)
            week_later = today + datetime.timedelta(weeks=1)

            grouped_reservations = {
                'today': [],
                'tomorrow': [],
                'after_tomorrow': [],
                'this_week': []
            }

            for reservation in reservations:
                if reservation[4] is None:
                    continue
                    
                try:
                    reservation_day = datetime.datetime.strptime(reservation[4], "%Y-%m-%d").date()
                    
                    reservation_data = {
                        'id': reservation[0],
                        'fullname': reservation[1],
                        'time': reservation[2],
                        'status': reservation[3],
                        'day': reservation_day
                    }

                    if reservation_data['day'] == today:
                        grouped_reservations['today'].append(reservation_data)
                    elif reservation_data['day'] == tomorrow:
                        grouped_reservations['tomorrow'].append(reservation_data)
                    elif reservation_data['day'] == after_tomorrow:
                        grouped_reservations['after_tomorrow'].append(reservation_data)
                    elif today < reservation_data['day'] <= week_later:
                        grouped_reservations['this_week'].append(reservation_data)
                        
                except ValueError:
                    continue

            result = {
                'today': grouped_reservations['today'],
                'tomorrow': grouped_reservations['tomorrow'],
                'after_tomorrow': grouped_reservations['after_tomorrow'],
                'this_week': grouped_reservations['this_week']
            }
            if all(not grouped_reservations[key] for key in grouped_reservations):
                return None
            return result

    except Exception as e:
        logging.critical(f"Problème d'exécution {e}", exc_info=True)
        return None


def get_all_reservations():
    try:
        with sqlite3.connect(rdv_db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM reservation_data ORDER BY day DESC, time')
            reservations = cursor.fetchall()

            result = []

            for reservation in reservations:
                reservation_dict = {
                    'id': reservation[0],
                    'country': reservation[1],
                    'phone': reservation[2],
                    'fullname': reservation[3],
                    'experience': reservation[4],
                    'employees': reservation[5],
                    'revenue': reservation[6],
                    'expectations': reservation[7],
                    'consultation': reservation[8],
                    'day': reservation[9],
                    'time': reservation[10],
                    'full_datetime': reservation[11],
                    'status': reservation[12]
                }
                result.append(reservation_dict)
            return result

    except Exception as e:
        logging.critical(f"Problème d'exécution {e}", exc_info=True)
        return None
    
def get_reservation_by_id(rdv_id):
    try:
        if rdv_id is None:
            logging.warning("get_reservation_by_id called with None rdv_id")
            return None
            
        with sqlite3.connect(rdv_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM reservation_data WHERE id = ?', (rdv_id,))
            reservation = cursor.fetchone()

            if reservation:
                # Log successful retrieval
                logging.info(f"Retrieved reservation for ID {rdv_id}")
                return {
                    'id': reservation[0],
                    'country': reservation[1],
                    'phone': reservation[2],
                    'fullname': reservation[3],
                    'experience': reservation[4],
                    'employees': reservation[5],
                    'revenue': reservation[6],
                    'expectations': reservation[7],
                    'consultation': reservation[8],
                    'day': reservation[9],
                    'time': reservation[10],
                    'full_datetime': reservation[11],
                    'status': reservation[12]
                }
            
            # Log when no reservation found
            logging.warning(f"No reservation found for ID {rdv_id}")
            return None
            
    except Exception as e:
        logging.critical(f"Database error in get_reservation_by_id: {e}", exc_info=True)
        return None
    
def update_reservation(rdv_id, data):
    try:
        with sqlite3.connect(rdv_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE reservation_data
                SET phone = ?, 
                    fullname = ?, 
                    day = ?, 
                    time = ?, 
                    status = ?
                WHERE id = ?
            ''', (data['phone_number'], 
                  data['fullname'], 
                  data['day'], 
                  data['time'], 
                  data['status'],
                  rdv_id))
            conn.commit()
            return True
    except Exception as e:
        logging.critical(f"Problème d'exécution {e}", exc_info=True)
        return False

def get_dashboard_stats():
    try:
        with sqlite3.connect(rdv_db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM reservation_data')
            total_appointments = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM reservation_data WHERE status = "pending"')
            pending_appointments = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM reservation_data WHERE status = "confirmed"')
            confirmed_appointments = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM reservation_data WHERE status = "finish"')
            completed_appointments = cursor.fetchone()[0]

            return {
                'total': total_appointments,
                'pending': pending_appointments,
                'confirmed': confirmed_appointments,
                'completed': completed_appointments
            }
    except Exception as e:
        logging.critical(f"Problème d'exécution {e}", exc_info=True)
        return {
            'total': 0,
            'pending': 0,
            'completed': 0
        }
    

def delete_reservation_by_id(rdv_id: int) -> bool:
    try:
        with sqlite3.connect(rdv_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM reservation_data WHERE id = ?', (rdv_id,))
            conn.commit()

            if cursor.rowcount == 0:  # Si aucun enregistrement supprimé
                logging.warning(f"Aucun rendez-vous trouvé avec l'ID {rdv_id}")
                return False
            
            logging.info(f"Rendez-vous avec l'ID {rdv_id} supprimé avec succès")
            return True
    except Exception as e:
        logging.critical(f"Problème d'exécution {e}", exc_info=True)
        return False
