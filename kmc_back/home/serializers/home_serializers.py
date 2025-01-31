from rest_framework import serializers

from ..models.home_models import HomeSwiper, HomeDetails, FlashSale, GalleryImage, DemoBooking, DemoBookingPage

image_extensions = ['jpg', 'png', 'jpeg', 'gif']


class SwiperSerializer(serializers.ModelSerializer):
    is_video = serializers.SerializerMethodField()

    def get_is_video(self, swiper):
        swiper_slice_array = swiper.media.path.split('.')
        swiper_length = len(swiper_slice_array) - 1

        if swiper_slice_array[swiper_length:][0] in image_extensions:
            return False
        return True

    class Meta:
        model = HomeSwiper
        fields = "__all__"


class HomeDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeDetails
        exclude = ['id']

class FlashSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashSale
        fields = ['title', 'start_date', 'end_date', 'is_active']


class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = '__all__'


class DemoBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemoBooking
        fields = '__all__'
        
    def validate(self, attrs):
        if attrs.get('email'):
            attrs['email'] = attrs.get('email').lower()
        return attrs

class DemoBookingPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemoBookingPage
        fields = '__all__'