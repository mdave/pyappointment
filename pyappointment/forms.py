from django import forms

class BookingForm(forms.Form):
    name  = forms.CharField  (max_length = 50,
                              label      = 'Name',
                              required   = True)
    email = forms.EmailField (label      = 'E-mail',
                              required   = True)
    notes = forms.CharField  (label      = 'Notes (optional)',
                              widget     = forms.Textarea,
                              required   = False)
