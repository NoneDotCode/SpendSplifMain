import hashlib
import datetime
from backend.apps.taxes.xml_models.dpfdp7_epo2 import Pisemnost
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

def generate_xml(data: dict) -> str:
    dpfdp7_data = data["dpfdp7"]
    veta_d_data = dpfdp7_data["veta_d_element"]
    veta_p_data = dpfdp7_data.get("veta_p", {})
    veta_b_data = dpfdp7_data.get("veta_b", {})

    pisemnost = Pisemnost(
        dpfdp7=Pisemnost.Dpfdp7(
            veta_d_element=Pisemnost.Dpfdp7.VetaD(**veta_d_data),
            veta_p=Pisemnost.Dpfdp7.VetaP(**veta_p_data) if veta_p_data else None,
            veta_b=Pisemnost.Dpfdp7.VetaB(**veta_b_data) if veta_b_data else None,
        ),
        verze_sw="1.0",
        nazev_sw="SpendSplif",
    )

    serializer = XmlSerializer(config=SerializerConfig(pretty_print=False, xml_declaration=True))
    raw_xml = serializer.render(pisemnost)

    delka = len(raw_xml.encode("utf-8"))
    kc = hashlib.md5(raw_xml.encode("utf-8")).hexdigest()

    now = datetime.datetime.now()
    dic = veta_p_data.get("dic") or "0000000000" 
    nazev = f"DPFDP7-{dic}-{now.strftime('%Y%m%d-%H%M%S')}"
    c_ufo = int(veta_d_data.get("c_ufo_cil", 0))

    pisemnost.kontrola = Pisemnost.Kontrola(
        soubor=Pisemnost.Kontrola.Soubor(
            Delka=delka,
            KC=kc,
            Nazev=nazev,
            c_ufo=c_ufo
        )
    )

    final_serializer = XmlSerializer(config=SerializerConfig(pretty_print=True, xml_declaration=True))
    return final_serializer.render(pisemnost)
