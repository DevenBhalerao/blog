from django import forms


class VoteForm(forms.Form):
    user = forms.CharField(widget=forms.HiddenInput)
    content_type_upvote = forms.CharField(widget=forms.HiddenInput)
    object_id_upvote = forms.IntegerField(widget=forms.HiddenInput)
