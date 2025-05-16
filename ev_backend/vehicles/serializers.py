from rest_framework import serializers
from .models import Vehicle, VehicleCatalog

class VehicleCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleCatalog
        fields = '__all__'


class VehicleSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    # Show catalog as nested read-only field
    catalog = VehicleCatalogSerializer(read_only=True)

    # Provide catalog ID if selecting from existing
    catalog_id = serializers.PrimaryKeyRelatedField(
        queryset=VehicleCatalog.objects.all(),
        source='catalog',
        write_only=True,
        required=False # This field is optional
    )

    # Optional Custom fields for brand and model
    custom_brand = serializers.CharField(required=False, allow_blank=True)
    custom_model = serializers.CharField(required=False, allow_blank=True)


    class Meta:
        model = Vehicle
        fields = ['id', 'user', 'catalog', 'catalog_id', 'custom_brand', 'custom_model', 'registration_number']

    def validate(self, data):
        catalog = data.get('catalog')
        custom_brand = data.get('custom_brand')
        custom_model = data.get('custom_model')

        if not catalog and not (custom_brand and custom_model):
            raise serializers.ValidationError(
                "You must either select a catalog_id or provide both custom_brand and custom_model."
            )

        if catalog and (custom_brand or custom_model):
            raise serializers.ValidationError(
                "Provide either catalog_id or custom_brand/custom_model, not both."
            )

        return data