from django import forms
from .models import Document, Folder

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('file', 'name')

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 5 * 1024 * 1024:  # 5MB Limit
                raise forms.ValidationError("Die Datei ist zu groß. Maximal 5MB erlaubt.")
            if not file.name.endswith(('.pdf', '.docx')):
                raise forms.ValidationError("Ungültiges Dateiformat. Nur PDF und DOCX erlaubt.")
        return file

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ('name',)