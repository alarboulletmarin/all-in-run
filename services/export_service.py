import io
import uuid
from datetime import datetime, timedelta
from xml.dom import minidom
from xml.etree import ElementTree as ET

from ics import Calendar, Event
from ics.alarm import DisplayAlarm
from ics.grammar.parse import ContentLine
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from config.languages import (
    DAYS_TRANSLATIONS,
    SESSION_TYPE_TRANSLATIONS,
    PHASE_TRANSLATIONS
)
from models.plan import TrainingPlan
from models.session import SessionType, TrainingPhase
from utils.date_utils import format_date
from utils.time_converter import format_timedelta, format_pace


class ExportService:
    """Service d'exportation du plan d'entraînement"""

    def export_to_ics(self, plan: TrainingPlan, lang: str = "fr", options: dict = None) -> bytes:
        """
        Exporte le plan d'entraînement au format ICS (calendrier)

        Args:
            plan: Plan d'entraînement à exporter
            lang: Code de langue
            options: Options supplémentaires pour l'export
                - include_rest_days: Inclure les jours de repos (bool)
                - reminder_time: Minutes avant la séance pour le rappel (int)
                - start_time: Heure de début par défaut (int)
                - ics_calendar_name: Nom du calendrier (str)

        Returns:
            Contenu du fichier ICS en bytes
        """
        # Valeurs par défaut des options
        default_options = {
            "include_rest_days": False,
            "reminder_time": 30,
            "start_time": 18,
            "ics_calendar_name": "Training Plan"
        }
        
        # Fusionner avec les options fournies
        if options is None:
            options = {}
        
        for key, default_value in default_options.items():
            if key not in options:
                options[key] = default_value

        # Créer un nouveau calendrier avec les métadonnées requises
        calendar = Calendar()
        calendar.scale = 'GREGORIAN'
        calendar.method = 'PUBLISH'
        calendar.name = options["ics_calendar_name"]
        calendar.creator = 'All-in-Run Training Plan Generator'

        # Ajouter chaque séance comme un événement du calendrier
        for session_date, session in plan.sessions.items():
            if session.session_type == SessionType.REST and not options["include_rest_days"]:
                # Ignorer les jours de repos si l'option est désactivée
                continue

            # Créer un événement pour la séance
            event = Event()

            # ID unique - crucial pour iOS
            event.uid = str(uuid.uuid4())

            # Déterminer le titre de l'événement
            session_type_name = SESSION_TYPE_TRANSLATIONS.get(lang, {}).get(
                session.session_type.value,
                session.session_type.value
            )

            event.name = f"🏃 {session_type_name}"

            # Description détaillée
            description = []
            description.append(session.description)
            description.append("")

            if session.session_type != SessionType.REST:
                description.append(f"Distance: {session.total_distance} km")
                description.append(f"Durée estimée: {format_timedelta(session.total_duration, 'hms_text')}")

            # Ajouter les détails des blocs (si présents)
            if session.blocks:
                description.append("")
                description.append("Détail de la séance:")
                for i, block in enumerate(session.blocks, 1):
                    description.append(f"- Bloc {i}: {block.distance} km @ {format_pace(block.pace)} ({block.description})")

            event.description = "\n".join(description)

            # Date et heure (utiliser l'heure de début définie dans les options)
            start_time = datetime.combine(session_date, datetime.min.time().replace(hour=options["start_time"]))

            # La durée de l'événement doit être un timedelta pour ics
            duration = timedelta(minutes=max(30, int(session.total_duration.total_seconds() / 60)))

            event.begin = start_time
            event.duration = duration

            # Ajouter une alarme (rappel) avec le temps défini dans les options
            reminder_time = options["reminder_time"]
            alarm = DisplayAlarm(trigger=timedelta(minutes=-reminder_time))
            event.alarms.append(alarm)

            # Catégorie pour faciliter le filtrage
            event.categories = ['Training', 'Running']

            # Emplacement (optionnel, mais peut améliorer l'expérience)
            event.location = "Course à pied"

            # Ajouter l'événement au calendrier
            calendar.events.add(event)

        # Convertir le calendrier en chaîne ICS

        # Ajouter les propriétés spéciales X- au calendrier
        calendar.extra.append(
            ContentLine(name="X-WR-CALNAME", value=options['ics_calendar_name'])
        )
        calendar.extra.append(
            ContentLine(name="X-WR-CALDESC", value="Plan d'entraînement running généré par All-in-Run")
        )
        calendar.extra.append(
            ContentLine(name="X-WR-TIMEZONE", value="Europe/Paris")
        )
        
        # Ajouter des propriétés spécifiques à iOS
        calendar.extra.append(
            ContentLine(name="X-APPLE-CALENDAR-COLOR", value="#FF0000")
        )
        calendar.extra.append(
            ContentLine(name="X-APPLE-LOCAL-DEFAULT-ALARM", value="PT30M")
        )
        calendar.extra.append(
            ContentLine(name="X-APPLE-STRUCTURED-LOCATION", value=";;;")
        )
        
        ics_content = calendar.serialize()

        # Convertir en bytes avec l'encodage UTF-8 explicite
        return ics_content.encode("utf-8")

    def export_to_pdf(self, plan: TrainingPlan, lang: str = "fr", options: dict = None) -> bytes:
        """
        Exporte le plan d'entraînement au format PDF

        Args:
            plan: Plan d'entraînement à exporter
            lang: Code de langue
            options: Options supplémentaires pour l'export
                - include_charts: Inclure les graphiques (bool)
                - include_details: Inclure les détails (bool)
                - paper_size: Taille du papier (str: "A4", "Letter", "Legal")
                - orientation: Orientation (str: "portrait", "landscape")

        Returns:
            Contenu du fichier PDF en bytes
        """
        # Valeurs par défaut des options
        default_options = {
            "include_charts": True,
            "include_details": True,
            "paper_size": "A4",
            "orientation": "portrait"
        }

        # Fusionner avec les options fournies
        if options is None:
            options = {}

        for key, default_value in default_options.items():
            if key not in options:
                options[key] = default_value

        buffer = io.BytesIO()

        # Déterminer la taille de page
        page_size = A4  # Taille par défaut
        if options["paper_size"] == "Letter":
            from reportlab.lib.pagesizes import LETTER
            page_size = LETTER
        elif options["paper_size"] == "Legal":
            from reportlab.lib.pagesizes import LEGAL
            page_size = LEGAL

        # Appliquer l'orientation
        if options["orientation"] == "landscape":
            page_size = page_size[1], page_size[0]  # inverser largeur et hauteur

        # Créer le document PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=page_size,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )

        # Styles
        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        heading_style = styles["Heading2"]
        heading3_style = styles["Heading3"]
        normal_style = ParagraphStyle(
            'Normal',
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            spaceAfter=6,
            wordWrap='CJK'  # Permet le retour à la ligne automatique
        )

        # Créer le contenu du PDF
        content = []

        # Titre du document
        content.append(Paragraph(f"Plan d'entraînement - {plan.user_data.main_race.race_type.value}", title_style))
        content.append(Spacer(1, 0.5*cm))

        # Informations générales
        content.append(Paragraph("Informations générales", heading_style))

        general_info = [
            ["Date de début", format_date(plan.user_data.start_date, lang)],
            ["Date de course", format_date(plan.user_data.main_race.race_date, lang)],
            ["Nombre de semaines", str(plan.user_data.total_weeks)],
            ["Volume total", f"{plan.get_total_volume()} km"],
            ["Temps total estimé", format_timedelta(plan.get_total_duration(), 'hms_text')]
        ]

        general_table = Table(general_info, colWidths=[4*cm, None])
        general_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))

        content.append(general_table)
        content.append(Spacer(1, 0.5*cm))

        # Répartition des phases
        content.append(Paragraph("Phases d'entraînement", heading_style))

        phase_stats = plan.get_phase_stats()
        phase_info = [["Phase", "Semaines", "Volume", "Temps estimé"]]

        for phase in TrainingPhase:
            if phase in phase_stats:
                stats = phase_stats[phase]
                phase_name = PHASE_TRANSLATIONS.get(lang, {}).get(phase.value, phase.value)

                phase_info.append([
                    phase_name,
                    str(stats["num_weeks"]),
                    f"{stats['total_volume']} km",
                    format_timedelta(stats['total_duration'], 'hms_text')
                ])

        phase_table = Table(phase_info, colWidths=[4*cm, 2.5*cm, 3*cm, None])
        phase_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))

        content.append(phase_table)
        content.append(Spacer(1, 1*cm))

        # Plan détaillé par semaine
        if options["include_details"]:
            content.append(Paragraph("Plan détaillé", heading_style))

            sessions_by_week = plan.get_sessions_by_week()

            for week_num in sorted(sessions_by_week.keys()):
                week_start, week_end = plan.get_week_dates(week_num)

                # Déterminer la phase de la semaine
                week_phase = None
                for day in range(7):
                    day_date = week_start + timedelta(days=day)
                    day_phase = plan.get_phase_for_date(day_date)
                    if day_phase:
                        week_phase = day_phase
                        break

                # Traduire le nom de la phase
                phase_name = PHASE_TRANSLATIONS.get(lang, {}).get(
                    week_phase.value if week_phase else "",
                    week_phase.value if week_phase else ""
                )

                # Titre de la semaine avec la phase
                week_title = f"Semaine {week_num + 1} - {phase_name}: {format_date(week_start, lang, False)} - {format_date(week_end, lang, False)}"
                content.append(Paragraph(week_title, heading3_style))

                # Informations sur la semaine
                week_volume = plan.get_weekly_volume(week_num)
                week_duration = plan.get_weekly_duration(week_num)

                week_info = [
                    ["Volume", f"{week_volume} km"],
                    ["Temps estimé", format_timedelta(week_duration, 'hms_text')]
                ]

                week_table = Table(week_info, colWidths=[3*cm, None])
                week_table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('PADDING', (0, 0), (-1, -1), 6),
                ]))

                content.append(week_table)
                content.append(Spacer(1, 0.3*cm))

                # Tableau des séances de la semaine
                sessions_info = []
                sessions_info.append([
                    Paragraph("Type", normal_style),
                    Paragraph("Distance", normal_style),
                    Paragraph("Temps", normal_style),
                    Paragraph("Description", normal_style)
                ])

                # Trier les séances par jour de la semaine
                week_sessions = sorted(
                    sessions_by_week[week_num],
                    key=lambda s: s.session_date.weekday()
                )

                for session in week_sessions:
                    day_name = DAYS_TRANSLATIONS.get(lang, {}).get(
                        session.session_date.weekday(),
                        session.session_date.strftime("%A")
                    )

                    session_type_name = SESSION_TYPE_TRANSLATIONS.get(lang, {}).get(
                        session.session_type.value,
                        session.session_type.value
                    )

                    # Préfixer avec le jour de la semaine
                    full_type_name = f"{day_name}: {session_type_name}"

                    if session.session_type == SessionType.REST:
                        sessions_info.append([
                            Paragraph(full_type_name, normal_style),
                            Paragraph("-", normal_style),
                            Paragraph("-", normal_style),
                            Paragraph("Repos", normal_style)
                        ])
                    else:
                        # Utiliser Paragraph pour permettre le retour à la ligne automatique
                        sessions_info.append([
                            Paragraph(full_type_name, normal_style),
                            Paragraph(f"{session.total_distance} km", normal_style),
                            Paragraph(format_timedelta(session.total_duration, 'hms'), normal_style),
                            Paragraph(session.description, normal_style)
                        ])

                # Créer le tableau avec des largeurs de colonne ajustées
                # La 4e colonne (description) est plus large pour éviter les coupures
                sessions_table = Table(sessions_info, colWidths=[4*cm, 2*cm, 2.5*cm, 9*cm])
                sessions_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Aligner en haut pour le texte multiligne
                    ('PADDING', (0, 0), (-1, -1), 6),
                ]))

                content.append(sessions_table)
                content.append(Spacer(1, 0.7*cm))

        # Générer le PDF
        doc.build(content)

        # Récupérer le contenu du buffer
        buffer.seek(0)
        return buffer.getvalue()

    def export_to_json(self, plan: TrainingPlan) -> str:
        """
        Exporte le plan d'entraînement au format JSON

        Args:
            plan: Plan d'entraînement à exporter

        Returns:
            Chaîne JSON
        """
        return plan.to_json()

    def export_to_tcx(self, plan: TrainingPlan, lang: str = "fr") -> bytes:
        """
        Exporte le plan d'entraînement au format TCX pour montres Garmin

        Args:
            plan: Plan d'entraînement à exporter
            lang: Code de langue

        Returns:
            Contenu du fichier TCX en bytes
        """


        # Créer la structure XML de base
        root = ET.Element("TrainingCenterDatabase")
        root.set("xmlns", "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2")
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.set("xsi:schemaLocation", "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd")

        # Ajouter l'élément Workouts
        workouts = ET.SubElement(root, "Workouts")

        # Traiter chaque séance comme un workout séparé
        for session_date, session in plan.sessions.items():
            if session.session_type == SessionType.REST:
                # Ignorer les jours de repos
                continue

            # Créer l'entraînement
            workout = ET.SubElement(workouts, "Workout")
            workout.set("Sport", "Running")

            # Nom de la séance
            session_type_name = SESSION_TYPE_TRANSLATIONS.get(lang, {}).get(
                session.session_type.value,
                session.session_type.value
            )

            name = ET.SubElement(workout, "Name")
            name.text = f"{format_date(session_date, lang, False)} - {session_type_name}"

            # Optionnel: ajouter les notes/description
            notes = ET.SubElement(workout, "Notes")
            notes.text = session.description

            # Créer les étapes de l'entraînement
            step_id = 1

            # Si la séance a des blocs, les utiliser, sinon créer un bloc unique
            if session.blocks:
                for block in session.blocks:
                    # Créer un bloc d'entraînement
                    step = ET.SubElement(workout, "Step")
                    step.set("xsi:type", "Step_t")

                    # ID de l'étape
                    id_elem = ET.SubElement(step, "StepId")
                    id_elem.text = str(step_id)
                    step_id += 1

                    # Nom de l'étape
                    name = ET.SubElement(step, "Name")
                    name.text = block.description

                    # Durée de l'étape (en distance)
                    duration = ET.SubElement(step, "Duration")
                    duration.set("xsi:type", "Distance_t")

                    meters = ET.SubElement(duration, "Meters")
                    meters.text = str(int(block.distance * 1000))

                    # Intensité (Active ou Rest)
                    intensity = ET.SubElement(step, "Intensity")
                    intensity.text = "Active"

                    # Allure cible
                    target = ET.SubElement(step, "Target")
                    target.set("xsi:type", "Speed_t")

                    speed_zone = ET.SubElement(target, "SpeedZone")

                    # Convertir l'allure (min/km) en vitesse (m/s)
                    pace_seconds = block.pace.total_seconds()
                    speed_mps = 1000 / pace_seconds  # mètres par seconde

                    # Créer une plage d'allures (+/- 5%)
                    low = ET.SubElement(speed_zone, "LowInMetersPerSecond")
                    low.text = f"{speed_mps * 0.95:.2f}"

                    high = ET.SubElement(speed_zone, "HighInMetersPerSecond")
                    high.text = f"{speed_mps * 1.05:.2f}"
            else:
                # Si pas de blocs, créer une étape unique pour la session complète
                step = ET.SubElement(workout, "Step")
                step.set("xsi:type", "Step_t")

                id_elem = ET.SubElement(step, "StepId")
                id_elem.text = "1"

                name = ET.SubElement(step, "Name")
                name.text = session_type_name

                duration = ET.SubElement(step, "Duration")
                duration.set("xsi:type", "Distance_t")

                meters = ET.SubElement(duration, "Meters")
                meters.text = str(int(session.total_distance * 1000))

                intensity = ET.SubElement(step, "Intensity")
                intensity.text = "Active"

                # Pour une séance simple, utiliser l'allure EF comme référence
                target = ET.SubElement(step, "Target")
                target.set("xsi:type", "Speed_t")

                speed_zone = ET.SubElement(target, "SpeedZone")

                # Estimer la vitesse moyenne
                avg_speed = 1000 / plan.user_data.pace_marathon.total_seconds()

                low = ET.SubElement(speed_zone, "LowInMetersPerSecond")
                low.text = f"{avg_speed * 0.95:.2f}"

                high = ET.SubElement(speed_zone, "HighInMetersPerSecond")
                high.text = f"{avg_speed * 1.05:.2f}"

            # Élément ScheduledOn obligatoire - date de la séance
            scheduled = ET.SubElement(workout, "ScheduledOn")
            scheduled.text = session_date.strftime("%Y-%m-%d")

        # Convertir l'arbre ElementTree en chaîne XML bien formatée
        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8")

        return pretty_xml