from django import forms
from .models import Params


class DeckForm(forms.Form):
    deck = forms.CharField(
        label="",
        widget=forms.Textarea(
            attrs={
                "id": "deck_input",
                "cols": "100",
                "rows": "10",
                "placeholder": "Put deck here!",
            }
        ),
    )

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        last_entry = self.deck
        form = form.base_fields["Name"].widget.attrs["value"] = last_entry


class ParamsForm(forms.ModelForm):
    class Meta:
        model = Params
        fields = "__all__"
