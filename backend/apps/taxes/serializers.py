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
    c_ufo_cil = serializers.IntegerField(required=False, min_value=10, max_value=9999)
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
        max_digits=16, 
        decimal_places=2, 
        required=False,
        error_messages={
            'max_digits': 'Maximum 16 digits allowed',
            'max_decimal_places': 'Maximum 2 decimal places allowed'
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
        if value is not None and (value < 10 or value > 9999):
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
    jmeno = serializers.CharField(
        max_length=30,
        error_messages={
            'max_length': 'Maximum 30 characters allowed for first name'
        }
    )
    prijmeni = serializers.CharField(
        max_length=36,
        error_messages={
            'max_length': 'Maximum 36 characters allowed for last name'
        }
    )
    dic = serializers.CharField(
        max_length=10,
        error_messages={
            'max_length': 'Maximum 10 characters allowed for DIC'
        }
    )
    email = serializers.EmailField(
        max_length=255,
        error_messages={
            'max_length': 'Maximum 255 characters allowed for email',
            'invalid': 'Enter a valid email address'
        }
    )
    c_pracufo = serializers.IntegerField(
        max_value=9999,
        error_messages={
            'max_value': 'Maximum 4 digits allowed for c_pracufo'
        }
    )
    naz_obce = serializers.CharField(
        max_length=48,
        error_messages={
            'max_length': 'Maximum 48 characters allowed for city name'
        }
    )
    psc = serializers.CharField(
        max_length=10,
        error_messages={
            'max_length': 'Maximum 10 characters allowed for postal code'
        }
    )
    ulice = serializers.CharField(
        max_length=38,
        error_messages={
            'max_length': 'Maximum 38 characters allowed for street'
        }
    )
    c_pop = serializers.IntegerField(
        max_value=999999,
        error_messages={
            'max_value': 'Maximum 6 digits allowed for house number'
        }
    )
    c_orient = serializers.CharField(
        max_length=4,
        allow_blank=True,
        required=False,
        error_messages={
            'max_length': 'Maximum 4 characters allowed for orientation number'
        }
    )
    k_stat = serializers.CharField(
        max_length=2,
        error_messages={
            'max_length': 'Maximum 2 characters allowed for country code'
        }
    )
    stat = serializers.CharField(
        max_length=25,
        error_messages={
            'max_length': 'Maximum 25 characters allowed for country name'
        }
    )

    def validate_dic(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("DIC must contain only digits")
        return value

    def validate_psc(self, value):
        if not value.replace(' ', '').isdigit():
            raise serializers.ValidationError("Postal code must contain only digits and spaces")
        return value

class VetaOSerializer(serializers.Serializer):
    kc_zd7 = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed for kc_zd7',
            'invalid': 'Enter a valid number'
        }
    )
    kc_zakldan23 = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed for kc_zakldan23',
            'invalid': 'Enter a valid number'
        }
    )
    kc_zakldan = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed for kc_zakldan',
            'invalid': 'Enter a valid number'
        }
    )
    kc_uhrn = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed for kc_uhrn',
            'invalid': 'Enter a valid number'
        }
    )

class VetaSSerializer(serializers.Serializer):
    kc_zdsniz = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed',
            'invalid': 'Enter a valid number'
        }
    )
    kc_zdzaokr = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed',
            'invalid': 'Enter a valid number'
        }
    )
    da_dan16 = serializers.DecimalField(
        max_digits=25,
        decimal_places=11,
        error_messages={
            'max_digits': 'Maximum 14 digits before decimal point allowed',
            'max_decimal_places': 'Maximum 11 decimal places allowed',
            'invalid': 'Enter a valid number'
        }
    )

    def validate_da_dan16(self, value):
        integer_part = str(value).split('.')[0]
        if len(integer_part) > 14:
            raise serializers.ValidationError("Maximum 14 digits before decimal point allowed")
        return value

class VetaBSerializer(serializers.Serializer):
    priloha1 = serializers.CharField()

class VetaTSerializer(serializers.Serializer):
    c_nace = serializers.CharField(
        max_length=6,
        error_messages={
            'max_length': 'Maximum 6 digits allowed for NACE code'
        }
    )
    kc_prij7 = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed for kc_prij7',
            'invalid': 'Enter a valid number for kc_prij7'
        }
    )
    kc_zd7p = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed for kc_zd7p',
            'invalid': 'Enter a valid number for kc_zd7p'
        }
    )
    kc_hosp_rozd = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed for kc_hosp_rozd',
            'invalid': 'Enter a valid number for kc_hosp_rozd'
        }
    )
    kc_cisobr = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed for kc_cisobr',
            'invalid': 'Enter a valid number for kc_cisobr'
        }
    )
    kc_vyd7 = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        error_messages={
            'max_digits': 'Maximum 14 digits allowed for kc_vyd7',
            'invalid': 'Enter a valid number for kc_vyd7'
        }
    )
    uc_soust = serializers.CharField(
        max_length=1,
        error_messages={
            'max_length': 'uc_soust must be exactly 1 character'
        }
    )

    def validate_c_nace(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("NACE code must contain only digits")
        if len(value) > 6:
            raise serializers.ValidationError("Maximum 6 digits allowed for NACE code")
        return value

    def validate_uc_soust(self, value):
        if value not in ['1', '2']:
            raise serializers.ValidationError("uc_soust must be either 'A' or 'N'")
        return value

class FormDataSerializer(serializers.Serializer):
    VetaD = VetaDSerializer()
    VetaP = VetaPSerializer()
    VetaO = VetaOSerializer()
    VetaT = VetaTSerializer()
    VetaS = VetaSSerializer()
    VetaB = VetaBSerializer()
