import io
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from django.http import FileResponse
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

from backend.apps.taxes.xml_models.dpfdp7_epo2 import Pisemnost
from backend.apps.taxes.serializers import FormDataSerializer
from backend.apps.taxes.xml_models.pdf_generator import generate_pdf
from backend.apps.taxes.xml_models.xml_generator import generate_xml

class GenerateXMLAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser]
    serializer_class = FormDataSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        validated_data = serializer.validated_data
        file, filename_or_error = generate_xml(validated_data)

        if file:
            return FileResponse(file, as_attachment=True, filename=filename_or_error)
        return Response({"error": filename_or_error}, status=400)


class GeneratePDFAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser]
    serializer_class = FormDataSerializer

    def post(self, request, *args, **kwargs):
        serializer = FormDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        pdf_buffer = generate_pdf(serializer.validated_data)
        return FileResponse(pdf_buffer, as_attachment=True, filename="danove_priznani.pdf")
