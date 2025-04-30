import streamlit as st
from utils.i18n import _ as translate

def render_drag_drop_calendar(sessions):
    """
    Affiche le calendrier avec support du glisser-déposer
    
    Args:
        sessions (list): Liste des séances d'entraînement
    """
    st.markdown("""
    <style>
    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 8px;
        margin-top: 20px;
    }
    .calendar-day {
        min-height: 100px;
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        background-color: #fff;
    }
    .calendar-day-header {
        font-weight: bold;
        margin-bottom: 8px;
        padding-bottom: 4px;
        border-bottom: 1px solid #eee;
    }
    .session-item {
        padding: 4px 8px;
        margin: 4px 0;
        border-radius: 4px;
        background-color: #e3f2fd;
        cursor: move;
        user-select: none;
    }
    .session-item.dragging {
        opacity: 0.5;
    }
    .drop-target {
        min-height: 20px;
        margin: 4px 0;
        border: 2px dashed #ccc;
        border-radius: 4px;
    }
    .drop-target.active {
        border-color: #2196f3;
        background-color: rgba(33, 150, 243, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # JavaScript pour le glisser-déposer
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const sessions = document.querySelectorAll('.session-item');
        const days = document.querySelectorAll('.calendar-day');
        
        sessions.forEach(session => {
            session.setAttribute('draggable', true);
            
            session.addEventListener('dragstart', function(e) {
                e.dataTransfer.setData('text/plain', this.id);
                this.classList.add('dragging');
            });
            
            session.addEventListener('dragend', function() {
                this.classList.remove('dragging');
            });
        });
        
        days.forEach(day => {
            day.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.classList.add('active');
            });
            
            day.addEventListener('dragleave', function() {
                this.classList.remove('active');
            });
            
            day.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('active');
                
                const sessionId = e.dataTransfer.getData('text/plain');
                const session = document.getElementById(sessionId);
                
                if (session) {
                    this.appendChild(session);
                    // Envoyer la nouvelle date au serveur
                    const dayDate = this.getAttribute('data-date');
                    window.parent.postMessage({
                        type: 'session_moved',
                        sessionId: sessionId,
                        newDate: dayDate
                    }, '*');
                }
            });
        });
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Afficher le calendrier
    st.markdown('<div class="calendar-grid">', unsafe_allow_html=True)
    
    # En-têtes des jours
    days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    for day in days:
        st.markdown(f'<div class="calendar-day-header">{day}</div>', unsafe_allow_html=True)
    
    # Jours du mois
    # TODO: Générer les jours du mois en cours
    for day in range(1, 32):
        date = f"2024-03-{day:02d}"
        st.markdown(f'''
        <div class="calendar-day" data-date="{date}">
            <div class="calendar-day-header">{day}</div>
            {render_day_sessions(date, sessions)}
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_day_sessions(date, sessions):
    """
    Rendu des séances pour un jour donné
    
    Args:
        date (str): Date au format YYYY-MM-DD
        sessions (list): Liste des séances
        
    Returns:
        str: HTML des séances
    """
    day_sessions = [s for s in sessions if s["date"] == date]
    html = ""
    
    for session in day_sessions:
        html += f'''
        <div class="session-item" id="session-{session['id']}">
            {session['type']} - {session['duration']}min
        </div>
        '''
    
    return html

def handle_session_move(session_id, new_date):
    """
    Gère le déplacement d'une séance
    
    Args:
        session_id (str): ID de la séance
        new_date (str): Nouvelle date au format YYYY-MM-DD
    """
    # TODO: Mettre à jour la date de la séance dans la base de données
    st.success(translate("session_moved", "ui")) 