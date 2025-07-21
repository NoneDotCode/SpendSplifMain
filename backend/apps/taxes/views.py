import io
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from django.http import FileResponse
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

from backend.apps.taxes.xml_models.dpfdp7_epo2 import Pisemnost

class GenerateXMLAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        data = request.data

        try:
            pisemnost = Pisemnost(
                verze_sw="1.0.0",
                nazev_sw="SpendSplif",
                dpfdp7=Pisemnost.Dpfdp7(
                    verze_pis="01.01",
                    veta_d_element=Pisemnost.Dpfdp7.VetaD(**data.get("VetaD", {})),
                    veta_p=Pisemnost.Dpfdp7.VetaP(**data.get("VetaP", {})),
                    veta_o=Pisemnost.Dpfdp7.VetaO(**data.get("VetaO", {})),
                    veta_s=Pisemnost.Dpfdp7.VetaS(**data.get("VetaS", {})),
                    veta_b_element=Pisemnost.Dpfdp7.VetaB(**data.get("VetaB", {})),
                    veta_t=Pisemnost.Dpfdp7.VetaT(**data.get("VetaT", {})),
                ),
                kontrola=None
            )

            config = SerializerConfig(pretty_print=True, xml_declaration=True, encoding="utf-8")
            serializer = XmlSerializer(config=config)
            xml_content = serializer.render(pisemnost)

            filename = f"DPFDP7-{data['VetaP']['dic']}.xml"
            file = io.BytesIO(xml_content.encode("utf-8"))
            response = FileResponse(file, as_attachment=True, filename=filename)
            return response

        except Exception as e:
            return Response({"error": str(e)}, status=400)
