# xml_generator.py
import io
from rest_framework.response import Response
from backend.apps.taxes.xml_models.dpfdp7_epo2 import Pisemnost
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig


def generate_xml(validated_data):
    """
    Генерирует XML файл на основе валидированных данных
    Возвращает FileResponse или Response с ошибкой
    """
    try:
        pisemnost = Pisemnost(
            verze_sw="1.0.0",
            nazev_sw="SpendSplif",
            dpfdp7=Pisemnost.Dpfdp7(
                verze_pis="01.01",
                veta_d_element=Pisemnost.Dpfdp7.VetaD(**validated_data["VetaD"]),
                veta_p=Pisemnost.Dpfdp7.VetaP(**validated_data["VetaP"]),
                veta_o=Pisemnost.Dpfdp7.VetaO(**validated_data["VetaO"]),
                veta_s=Pisemnost.Dpfdp7.VetaS(**validated_data["VetaS"]),
                veta_b_element=Pisemnost.Dpfdp7.VetaB(**validated_data["VetaB"]),
                veta_t=Pisemnost.Dpfdp7.VetaT(**validated_data["VetaT"]),
            ),
            kontrola=None
        )

        config = SerializerConfig(pretty_print=True, xml_declaration=True, encoding="utf-8")
        serializer = XmlSerializer(config=config)
        xml_content = serializer.render(pisemnost)

        filename = f"DPFDP7-{validated_data['VetaP']['dic']}.xml"
        file = io.BytesIO(xml_content.encode("utf-8"))
        return file, filename

    except Exception as e:
        return None, str(e)
    