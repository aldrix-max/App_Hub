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
