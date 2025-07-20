from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from django.utils.timezone import now
from .models import Transaction, Categorie, BudgetMensuel
from datetime import datetime
from textwrap import wrap
from decimal import Decimal

def generate_monthly_summary_pdf(mois, utilisateur):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 2 * cm
    left_margin = 2 * cm

    # En-tête
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(left_margin, y, "Rapport Mensuel de Trésorerie")
    y -= 1.2 * cm

    # Infos générales
    date_obj = datetime.strptime(mois, "%Y-%m")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(left_margin, y, f"Période couverte : {date_obj.strftime('%B %Y')}")
    y -= 0.5 * cm
    pdf.drawString(left_margin, y, f"Responsable financier : {utilisateur}")
    y -= 0.5 * cm
    pdf.drawString(left_margin, y, f"Date de génération : {now().strftime('%d %B %Y')}")
    y -= 1 * cm

    # Budget défini
    try:
        budget_obj = BudgetMensuel.objects.get(mois=mois)
        budget_mensuel = float(budget_obj.montant_total)
    except BudgetMensuel.DoesNotExist:
        budget_mensuel = 0.0

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left_margin, y, "2. Budget Défini")
    y -= 0.5 * cm
    pdf.setFont("Helvetica", 10)
    pdf.drawString(left_margin + 0.5 * cm, y, f"Budget pour {date_obj.strftime('%B %Y')} : {budget_mensuel:,.0f} €")
    y -= 1 * cm

    # Encaissements
    entrees = Transaction.objects.filter(
        date__year=date_obj.year,
        date__month=date_obj.month,
        categorie__type="ENTREE"
    ).select_related("categorie")

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left_margin, y, "3. Encaissements")
    y -= 0.6 * cm
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(left_margin + 0.5 * cm, y, "Source")
    pdf.drawString(left_margin + 5.5 * cm, y, "Montant (€)")
    pdf.drawString(left_margin + 9.5 * cm, y, "Date")
    pdf.drawString(left_margin + 13.5 * cm, y, "Description")
    y -= 0.5 * cm

    total_entrees = 0.0
    pdf.setFont("Helvetica", 9)
    for e in entrees:
        description = e.description or ""
        desc_lines = wrap(description, width=45)
        for i, line in enumerate(desc_lines):
            if y < 2.5 * cm:
                pdf.showPage()
                y = height - 2 * cm
                pdf.setFont("Helvetica", 9)
            if i == 0:
                pdf.drawString(left_margin + 0.5 * cm, y, e.categorie.nom)
                pdf.drawString(left_margin + 5.5 * cm, y, f"{float(e.montant):,.0f}")
                pdf.drawString(left_margin + 9.5 * cm, y, e.date.strftime("%d/%m/%Y"))
            pdf.drawString(left_margin + 13.5 * cm, y, line)
            y -= 0.4 * cm
        total_entrees += float(e.montant)

    pdf.setFont("Helvetica-Bold", 10)
    y -= 0.3 * cm
    pdf.drawString(left_margin + 0.5 * cm, y, f"Total encaissements : {total_entrees:,.0f} €")
    y -= 1 * cm

    # Décaissements
    depenses = Transaction.objects.filter(
        date__year=date_obj.year,
        date__month=date_obj.month,
        categorie__type="DEPENSE"
    ).select_related("categorie")

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left_margin, y, "4. Décaissements")
    y -= 0.6 * cm
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(left_margin + 0.5 * cm, y, "Type")
    pdf.drawString(left_margin + 5.5 * cm, y, "Montant (€)")
    pdf.drawString(left_margin + 9.5 * cm, y, "Date")
    pdf.drawString(left_margin + 13.5 * cm, y, "Description")
    y -= 0.5 * cm

    total_depenses = 0.0
    pdf.setFont("Helvetica", 9)
    for d in depenses:
        description = d.description or ""
        desc_lines = wrap(description, width=45)
        for i, line in enumerate(desc_lines):
            if y < 2.5 * cm:
                pdf.showPage()
                y = height - 2 * cm
                pdf.setFont("Helvetica", 9)
            if i == 0:
                pdf.drawString(left_margin + 0.5 * cm, y, d.categorie.nom)
                pdf.drawString(left_margin + 5.5 * cm, y, f"{float(d.montant):,.0f}")
                pdf.drawString(left_margin + 9.5 * cm, y, d.date.strftime("%d/%m/%Y"))
            pdf.drawString(left_margin + 13.5 * cm, y, line)
            y -= 0.4 * cm
        total_depenses += float(d.montant)

    pdf.setFont("Helvetica-Bold", 10)
    y -= 0.3 * cm
    pdf.drawString(left_margin + 0.5 * cm, y, f"Total décaissements : {total_depenses:,.0f} €")
    y -= 1 * cm

    # Solde final
    solde_final = budget_mensuel + total_entrees - total_depenses
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left_margin, y, "5. Solde Final")
    y -= 0.5 * cm
    pdf.setFont("Helvetica", 10)
    pdf.drawString(left_margin + 0.5 * cm, y, f"Solde au 30 {date_obj.strftime('%B')} : {solde_final:,.0f} €")
    y -= 1 * cm

    # Analyse
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left_margin, y, "6. Analyse et Commentaires")
    y -= 0.6 * cm
    variation = solde_final - budget_mensuel
    pdf.setFont("Helvetica", 10)
    pdf.drawString(left_margin + 0.5 * cm, y, f"Variation : {variation:+,.0f} € par rapport au budget initial")
    y -= 0.5 * cm
    pdf.drawString(left_margin + 0.5 * cm, y, "Dépenses totales à surveiller si elles dépassent le budget")

    pdf.save()
    buffer.seek(0)
    return buffer


def generate_agent_report_pdf(mois, agent):
    """Génère un PDF détaillé pour un agent spécifique"""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 2 * cm
    left_margin = 2 * cm

    # En-tête
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(left_margin, y, f"Rapport Mensuel - {agent.user.get_full_name()}")
    y -= 1.2 * cm

    # Infos générales
    date_obj = datetime.strptime(mois, "%Y-%m")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(left_margin, y, f"Période : {date_obj.strftime('%B %Y')}")
    y -= 0.5 * cm
    pdf.drawString(left_margin, y, f"Rôle : {agent.get_role_display()}")
    y -= 0.5 * cm
    pdf.drawString(left_margin, y, f"Service : {agent.service or 'Non spécifié'}")
    y -= 1 * cm

    # Budget de l'agent
    try:
        budget = BudgetMensuel.objects.get(mois=mois, utilisateur=agent.user)
        budget_montant = float(budget.montant_total)
        pdf.drawString(left_margin, y, f"Budget mensuel : {budget_montant:,.2f} €")
    except BudgetMensuel.DoesNotExist:
        budget_montant = 0
        pdf.drawString(left_margin, y, "Aucun budget défini pour ce mois")
    y -= 1 * cm

    # Transactions de l'agent
    transactions = Transaction.objects.filter(
        utilisateur=agent.user,
        date__year=date_obj.year,
        date__month=date_obj.month
    ).select_related('categorie').order_by('-date')

    # Tableau des transactions
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left_margin, y, "Transactions du mois :")
    y -= 0.8 * cm

    # En-têtes du tableau
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(left_margin, y, "Date")
    pdf.drawString(left_margin + 3*cm, y, "Type")
    pdf.drawString(left_margin + 6*cm, y, "Catégorie")
    pdf.drawString(left_margin + 10*cm, y, "Montant")
    pdf.drawString(left_margin + 14*cm, y, "Description")
    y -= 0.6 * cm

    # Lignes du tableau
    pdf.setFont("Helvetica", 9)
    total_depenses = 0
    total_entrees = 0

    for tr in transactions:
        if y < 3 * cm:  # Nouvelle page si on arrive en bas
            pdf.showPage()
            y = height - 2 * cm
            pdf.setFont("Helvetica", 9)

        pdf.drawString(left_margin, y, tr.date.strftime("%d/%m/%Y"))
        pdf.drawString(left_margin + 3*cm, y, tr.get_type_display())
        pdf.drawString(left_margin + 6*cm, y, tr.categorie.nom)
        montant = float(tr.montant)
        pdf.drawString(left_margin + 10*cm, y, f"{montant:,.2f} €")
        
        if tr.description:
            desc_lines = wrap(tr.description, width=40)
            for line in desc_lines:
                pdf.drawString(left_margin + 14*cm, y, line)
                y -= 0.4 * cm
        else:
            y -= 0.4 * cm

        if tr.type == "DEPENSE":
            total_depenses += montant
        else:
            total_entrees += montant

    # Totaux
    y -= 1 * cm
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(left_margin, y, f"Total dépenses : {total_depenses:,.2f} €")
    y -= 0.5 * cm
    pdf.drawString(left_margin, y, f"Total entrées : {total_entrees:,.2f} €")
    y -= 0.5 * cm
    pdf.drawString(left_margin, y, f"Solde final : {(budget_montant + total_entrees - total_depenses):,.2f} €")

    pdf.save()
    buffer.seek(0)
    return buffer

def generate_global_report_pdf(mois):
    from io import BytesIO
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.units import cm, inch
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib import colors
    from datetime import datetime
    from django.db.models import Sum, Q
    from .models import Transaction, Agent
    from reportlab.lib.enums import TA_CENTER

    try:
        # 1. Initialisation du document PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, 
                              pagesize=A4,
                              rightMargin=inch/2,
                              leftMargin=inch/2,
                              topMargin=inch/2,
                              bottomMargin=inch/2)

        # 2. Styles
        styles = getSampleStyleSheet()
        style_title = styles['Title']
        style_heading = styles['Heading2']
        style_normal = styles['BodyText']

        # 3. Contenu du PDF
        content = []

        # 4. Titre
        date_obj = datetime.strptime(mois, "%Y-%m")
        title_text = f"Rapport Global - {date_obj.strftime('%B %Y')}"
        content.append(Paragraph(title_text, style_title))
        content.append(Paragraph("<br/><br/>", style_normal))

        # 5. Récupération des données
        transactions = Transaction.objects.filter(
            date__year=date_obj.year,
            date__month=date_obj.month
        ).select_related('utilisateur', 'categorie').order_by('date')

        # 6. Vérification des données
        if not transactions.exists():
            content.append(Paragraph("Aucune transaction pour cette période.", style_normal))
            doc.build(content)
            buffer.seek(0)
            return buffer

        # 7. Tableau des transactions
        data = [['Date', 'Agent', 'Type', 'Catégorie', 'Montant', 'Description']]
        
        for tr in transactions:
            agent_name = f"{tr.utilisateur.last_name} {tr.utilisateur.first_name}"
            data.append([
                tr.date.strftime('%d/%m/%Y'),
                agent_name,
                'Entrée' if tr.type == 'ENTREE' else 'Dépense',
                tr.categorie.nom,
                f"{float(tr.montant):,.2f} €",
                tr.description or ''
            ])

        # 8. Création du tableau
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTSIZE', (0,1), (-1,-1), 8),
        ]))

        content.append(table)
        content.append(Paragraph("<br/><br/>", style_normal))

        # 9. Totaux
        total_entrees = transactions.filter(type='ENTREE').aggregate(Sum('montant'))['montant__sum'] or 0
        total_depenses = transactions.filter(type='DEPENSE').aggregate(Sum('montant'))['montant__sum'] or 0
        solde = total_entrees - total_depenses

        totals = [
            ['', 'Total Entrées', 'Total Dépenses', 'Solde'],
            ['', f"{float(total_entrees):,.2f} €", f"{float(total_depenses):,.2f} €", f"{float(solde):,.2f} €"]
        ]

        total_table = Table(totals)
        total_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))

        content.append(total_table)

        # 10. Génération finale
        doc.build(content)
        buffer.seek(0)
        return buffer

    except Exception as e:
        import traceback
        print(f"Erreur critique dans generate_global_report_pdf: {str(e)}")
        print(traceback.format_exc())
        raise