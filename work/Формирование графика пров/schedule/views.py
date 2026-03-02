from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from .models import ПроверкаЗнаний
import os


def скачать_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="grafik_proverki.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    elements = []

    # ===== ПОДКЛЮЧАЕМ TIMES NEW ROMAN =====
    font_path_regular = r"C:\Windows\Fonts\times.ttf"
    font_path_bold = r"C:\Windows\Fonts\timesbd.ttf"

    pdfmetrics.registerFont(TTFont('TimesNewRoman', font_path_regular))
    pdfmetrics.registerFont(TTFont('TimesNewRoman-Bold', font_path_bold))

    # ===== СТИЛИ =====
    стиль_заголовок = ParagraphStyle(
        name='Заголовок',
        fontName='TimesNewRoman-Bold',
        fontSize=14,
        alignment=1,
        spaceAfter=6
    )

    стиль_подзаголовок = ParagraphStyle(
        name='Подзаголовок',
        fontName='TimesNewRoman-Bold',
        fontSize=12,
        alignment=1,
        spaceAfter=12
    )

    стиль_ячейка = ParagraphStyle(
        name='Ячейка',
        fontName='TimesNewRoman',
        fontSize=9,
        alignment=1,  # по центру
    )

    стиль_подпись = ParagraphStyle(
        name='Подпись',
        fontName='TimesNewRoman',
        fontSize=10,
    )

    # ===== ЗАГОЛОВОК =====
    elements.append(Paragraph(
        "Факультет информационных технологий",
        стиль_заголовок
    ))

    elements.append(Paragraph(
        "График проверки остаточных знаний в ноябре-декабре 2024 года",
        стиль_подзаголовок
    ))

    elements.append(Spacer(1, 10))

    # ===== ДАННЫЕ =====
    данные = [[
        Paragraph("<b>№</b>", стиль_ячейка),
        Paragraph("<b>Группа</b>", стиль_ячейка),
        Paragraph("<b>Наименование профиля подготовки</b>", стиль_ячейка),
        Paragraph("<b>Наименование дисциплины</b>", стиль_ячейка),
        Paragraph("<b>Кафедра</b>", стиль_ячейка),
        Paragraph("<b>ФИО ППС</b>", стиль_ячейка),
        Paragraph("<b>Дата проведения</b>", стиль_ячейка),
        Paragraph("<b>Время проведения</b>", стиль_ячейка),
    ]]

    записи = ПроверкаЗнаний.objects.all()

    for i, z in enumerate(записи, start=1):
        данные.append([
            Paragraph(str(i), стиль_ячейка),
            Paragraph(z.группа.название, стиль_ячейка),
            Paragraph(z.профиль, стиль_ячейка),
            Paragraph(z.дисциплина.название, стиль_ячейка),
            Paragraph(z.преподаватель.кафедра.название, стиль_ячейка),
            Paragraph(z.преподаватель.фио, стиль_ячейка),
            Paragraph(z.дата_проведения.strftime("%d.%m.%Y"), стиль_ячейка),
            Paragraph(z.время_проведения.strftime("%H:%M"), стиль_ячейка),
        ])

    ширины = [
        10 * mm,
        20 * mm,
        35 * mm,
        35 * mm,
        20 * mm,
        30 * mm,
        20 * mm,
        20 * mm,
    ]

    таблица = Table(
        данные,
        colWidths=ширины,
        repeatRows=1
    )

    таблица.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.8, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    elements.append(таблица)

    elements.append(Spacer(1, 25))

    # ===== ПОДПИСЬ =====
    подпись = KeepTogether([
        Paragraph(
            "Декан факультета информационных технологий",
            стиль_подпись
        ),
        Spacer(1, 10),
        Paragraph(
            "__________________________        Д.Г. Демидов",
            стиль_подпись
        )
    ])

    elements.append(подпись)

    doc.build(elements)

    return response