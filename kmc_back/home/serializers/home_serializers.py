from rest_framework import serializers

from ..models.home_models import HomeSwiper, HomeDetails

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
