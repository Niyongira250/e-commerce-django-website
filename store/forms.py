from django import forms
from django.contrib.auth import get_user_model
from .models import YourAddress

from .models import Video

User = get_user_model()
class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'video_file']
        
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'phonenumber', 'profile_image', 'password']
        widgets = {
            'password': forms.PasswordInput(render_value=True),  # optional, helps preserve input visually
        }

    def clean_password(self):
        password = self.cleaned_data.get("password")
        return password


from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'feedback']

class YourAddressForm(forms.ModelForm):
    class Meta:
        model = YourAddress
        fields = ['street_address', 'city_state', 'country']