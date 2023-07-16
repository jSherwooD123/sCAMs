from django import forms
from .models import Camera, Room


class CameraAdd(forms.ModelForm):
    
    #Define the room field as a selection choice
    room = forms.ModelChoiceField(queryset=Room.objects.all())

    class Meta:
        model = Camera

        # Include all fields from the Camera model in the form
        fields = '__all__'

        # Exclude the 'active' and 'last_active' fields from the form
        exclude = ['active', 'last_active']

        # Change the label of 'c_name' field to 'Name'
        labels = {
            'c_name': 'Name',
        }

    def __init__(self, *args, **kwargs):
        super(CameraAdd, self).__init__(*args, **kwargs)
        # Set the queryset for the 'room' field to include all Room objects
        self.fields['room'].queryset = Room.objects.all()
        # Us3 'r_name' as a label for each choice in the drop down selection
        self.fields['room'].label_from_instance = lambda obj: obj.r_name

class RoomAdd(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        labels = {
            'r_name': 'Name',
        }
