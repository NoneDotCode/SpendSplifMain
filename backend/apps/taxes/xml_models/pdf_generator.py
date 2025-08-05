import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

def generate_pdf(validated_data):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', r'D:\IT\Projects\SpendSpl\backend\apps\taxes\xml_models\DejaVuSans.ttf'))
        font_name = 'DejaVuSans'
    except:
        try:
            pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
            font_name = 'Arial'
        except:
            font_name = 'Helvetica'

    y = height - 30 * mm
    x = 20 * mm

    p.setFont(font_name, 12)
    p.drawString(x, y, "Daňové přiznání fyzické osoby")
    y -= 15 * mm

    def draw_field(label, value):
        nonlocal y
        p.setFont(font_name, 10)
        p.drawString(x, y, f"{label}:")
        p.setFont(font_name, 10)
        p.drawString(x + 70 * mm, y, str(value))
        y -= 6 * mm
        if y < 100 * mm:
            p.showPage()
            y = height - 30 * mm

    def draw_section(fields_mapping, section_data):
        nonlocal y
        for field, label in fields_mapping.items():
            if field in section_data:
                draw_field(label, section_data[field])
        y -= 8 * mm

    veta_p_mapping = {
        'c_pracufo': 'Územní pracoviště',
        'dic': 'Daňové identifikační číslo',
        'prijmeni': 'Příjmení',
        'jmeno': 'Jméno',
        'email': 'Email',
        'naz_obce': 'Obec / Městská část',
        'ulice': 'Ulice/část obce',
        'c_pop': 'Číslo popisné',
        'c_orient': 'Číslo orientační',
        'psc': 'PSČ',
        'stat': 'Stát'
    }
    draw_section(veta_p_mapping, validated_data.get("VetaP", {}))

    veta_o_mapping = {
        'kc_zd7': 'Dílčí základ daně',
        'kc_zakldan23': 'Základ daně',
        'kc_zakldan': 'Základ daně po odečtení ztráty'
    }
    draw_section(veta_o_mapping, validated_data.get("VetaO", {}))

    veta_s_mapping = {
        'kc_zdsniz': 'Základ daně snížený',
        'da_dan16': 'Daň podle § 16 zákona'
    }
    draw_section(veta_s_mapping, validated_data.get("VetaS", {}))

    veta_t_mapping = {
        'c_nace': 'Název hlavní činnosti',
        'kc_cisobr': 'Roční úhrn čistého obratu',
        'kc_prij7': 'Příjmy podle § 7 zákona',
        'kc_vyd7': 'Výdaje související s příjmy',
        'kc_hosp_rozd': 'Rozdíl mezi příjmy a výdaji',
        'kc_zd7p': 'Dílčí základ daně z příjmů'
    }
    draw_section(veta_t_mapping, validated_data.get("VetaT", {}))

    veta_d_mapping = {
        'rok': 'Rok',
        'zdobd_od': 'Počátek zdaňovacího období',
        'zdobd_do': 'Konec zdaňovacího období',
        'da_slezap': 'Daň podle § 16 zákona',
        'da_celod13': 'Daň celkem zaokrouhlená',
        'kc_dztrata': 'Daňová ztráta',
        'da_slevy': 'Slevy celkem podle § 35',
        'kc_op15_1a': 'Základní sleva na poplatníka',
        'uhrn_slevy35ba': 'Úhrn slev na dani',
        'da_slevy35ba': 'Daň po uplatnění slev',
        'da_slevy35c': 'Daň po uplatnění slevy',
        'kc_dan_celk': 'Daň celkem',
        'kc_dan_po_db': 'Daň celkem po úpravě',
        'kc_db_po_odpd': 'Daňový bonus po odpočtu'
    }
    draw_section(veta_d_mapping, validated_data.get("VetaD", {}))

    y -= 10 * mm
    p.setFont(font_name, 14)
    dan_celk = validated_data.get("VetaD", {}).get("kc_dan_celk", "0")
    p.drawString(x, y, f"Celková částka splatné daně: {dan_celk} Kč")
    y -= 20 * mm

    p.setFont(font_name, 10)
    p.drawString(x, y, "Jméno a příjmení: __________________________")
    y -= 8 * mm
    p.drawString(x, y, "Datum narození: ____________________________")
    y -= 8 * mm
    p.drawString(x, y, f"Datum: {date.today().strftime('%d.%m.%Y')}")
    y -= 8 * mm
    p.drawString(x, y, "Podpis: ____________________________________")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
