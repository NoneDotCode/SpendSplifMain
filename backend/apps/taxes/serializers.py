from rest_framework import serializers

from rest_framework import serializers
from datetime import datetime


class VetaDSerializer(serializers.Serializer):
    rok = serializers.IntegerField(
        min_value=1000,
        max_value=9999,
        error_messages={
            'min_value': 'Year must be 4 digits',
            'max_value': 'Year must be 4 digits'
        }
    )
    pln_moc = serializers.CharField(max_length=1)
    audit = serializers.CharField(max_length=1)
    prop_zahr = serializers.CharField(max_length=1)
    dap_typ = serializers.CharField(max_length=1)
    k_uladis = serializers.CharField(max_length=3)
    c_ufo_cil = serializers.IntegerField(required=False, min_value=1000, max_value=9999)
    zdobd_od = serializers.CharField(required=False, max_length=10)
    zdobd_do = serializers.CharField(required=False, max_length=10)
    kc_op15_1a = serializers.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        required=False,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed'
        }
    )
    da_slevy = serializers.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        required=False,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed'
        }
    )
    da_slezap = serializers.DecimalField(
        max_digits=17, 
        decimal_places=14, 
        required=False,
        error_messages={
            'max_digits': 'Maximum 17 digits allowed',
            'max_decimal_places': 'Maximum 14 decimal places allowed'
        }
    )
    da_celod13 = serializers.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        required=False,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed'
        }
    )
    kc_dztrata = serializers.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        required=False,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed'
        }
    )
    uhrn_slevy35ba = serializers.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        required=False,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed'
        }
    )
    da_slevy35c = serializers.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        required=False,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed'
        }
    )
    kc_dan_po_db = serializers.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        required=False,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed'
        }
    )
    kc_zbyvpred = serializers.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        required=False,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed'
        }
    )
    da_slevy35ba = serializers.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        required=False,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed'
        }
    )
    kc_db_po_odpd = serializers.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        required=False,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed'
        }
    )
    kc_dan_celk = serializers.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        required=False,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed'
        }
    )

    def validate_rok(self, value):
        if value not in [2024, 2025]:
            raise serializers.ValidationError("Year must be either 2024 or 2025")
        return value

    def validate_pln_moc(self, value):
        if value not in ['A', 'N']:
            raise serializers.ValidationError("pln_moc must be either 'A' or 'N'")
        return value

    def validate_audit(self, value):
        if value not in ['A', 'N']:
            raise serializers.ValidationError("audit must be either 'A' or 'N'")
        return value

    def validate_prop_zahr(self, value):
        if value not in ['A', 'N']:
            raise serializers.ValidationError("prop_zahr must be either 'A' or 'N'")
        return value

    def validate_dap_typ(self, value):
        if value not in ['B', 'O', 'D', 'N']:
            raise serializers.ValidationError("dap_typ must be either 'B', 'O', 'D' or 'N'")
        return value

    def validate_k_uladis(self, value):
        if value != 'DPF':
            raise serializers.ValidationError("k_uladis must be 'DPF'")
        return value

    def validate_c_ufo_cil(self, value):
        if value is not None and (value < 1000 or value > 9999):
            raise serializers.ValidationError("c_ufo_cil must be 4 digits")
        return value

    def validate_zdobd_od(self, value):
        if value is not None:
            try:
                datetime.strptime(value, '%d.%m.%Y')
            except ValueError:
                raise serializers.ValidationError("zdobd_od must be in format DD.MM.YYYY")
        return value

    def validate_zdobd_do(self, value):
        if value is not None:
            try:
                datetime.strptime(value, '%d.%m.%Y')
            except ValueError:
                raise serializers.ValidationError("zdobd_do must be in format DD.MM.YYYY")
        return value

class VetaPSerializer(serializers.Serializer):
    jmeno = serializers.CharField()
    prijmeni = serializers.CharField()
    dic = serializers.CharField()
    email = serializers.EmailField()
    c_pracufo = serializers.IntegerField()
    naz_obce = serializers.CharField()
    psc = serializers.CharField()
    ulice = serializers.CharField()
    c_pop = serializers.IntegerField()
    c_orient = serializers.CharField(allow_blank=True, required=False)
    k_stat = serializers.CharField()
    stat = serializers.CharField()

class VetaOSerializer(serializers.Serializer):
    kc_zd7 = serializers.DecimalField(max_digits=15, decimal_places=2)
    kc_zakldan8 = serializers.DecimalField(max_digits=15, decimal_places=2)
    kc_zd9 = serializers.DecimalField(max_digits=15, decimal_places=2)
    kc_zd10 = serializers.DecimalField(max_digits=15, decimal_places=2)
    kc_uhrn = serializers.DecimalField(max_digits=15, decimal_places=2)

class VetaSSerializer(serializers.Serializer):
    c_nace = serializers.CharField()

class VetaBSerializer(serializers.Serializer):
    priloha1 = serializers.CharField()

class FormDataSerializer(serializers.Serializer):
    VetaD = VetaDSerializer()
    VetaP = VetaPSerializer()
    VetaO = VetaOSerializer()
    VetaS = VetaSSerializer()
    VetaB = VetaBSerializer()
