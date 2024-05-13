from django import forms
from django.forms import ModelForm
from .models import Community , Posting , PostType

# Create a venue form
class CommunityForm(ModelForm):
	class Meta:
		model = Community
		#fields = "__all__"
		fields = ('name','is_public','description')

		labels = {
			'name' : '',
			'is_public' : '',
			'description':''


		}
		
		widgets = {
			'name' : forms.TextInput(attrs = {'class':'form-control', 'placeholder' :'Community Name' }),
			'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
			'description' : forms.Textarea(attrs = {'class':'form-control', 'placeholder' :'Description' }),
			#'address' : forms.TextInput(attrs = {'class':'form-control', 'placeholder' :'Address' }),
			#'zip_code' : forms.TextInput(attrs = {'class':'form-control', 'placeholder' :'Zip Code' }),
			#'phone' : forms.TextInput(attrs = {'class':'form-control', 'placeholder' :'Phone Number' }),
			#'web' : forms.TextInput(attrs = {'class':'form-control', 'placeholder' :'Website' }),
			#'email_address' : forms.EmailInput(attrs = {'class':'form-control', 'placeholder' :'Email Address' }),
		}


class PostingForm(ModelForm):
	class Meta:
		model = Posting
		#fields = "__all__"
		fields = ('community','name','description')

		labels = {
			'community' : 'Community',
			'name' : '',
			'description' : '',

		}
		
		widgets = {
			'name' : forms.TextInput(attrs = {'class':'form-control', 'placeholder' :'Post Title' }),
			'community' : forms.Select(attrs = {'class':'form-select', 'placeholder' :'Community' }),
			'description' : forms.Textarea(attrs = {'class':'form-control', 'placeholder' :'Description' }),
			#'address' : forms.TextInput(attrs = {'class':'form-control', 'placeholder' :'Address' }),
			#'zip_code' : forms.TextInput(attrs = {'class':'form-control', 'placeholder' :'Zip Code' }),
			#'phone' : forms.TextInput(attrs = {'class':'form-control', 'placeholder' :'Phone Number' }),
			#'web' : forms.TextInput(attrs = {'class':'form-control', 'placeholder' :'Website' }),
			#'email_address' : forms.EmailInput(attrs = {'class':'form-control', 'placeholder' :'Email Address' }),
		}


class PostTypeForm(ModelForm):
    class Meta:
        model = PostType
        fields = ('field_name', 'field_type')
        widgets = {
            'field_type': forms.Select()
        }