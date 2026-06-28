from pathlib import Path

from django import forms
from django.utils.text import get_valid_filename

from .models import Document, validate_pdf_upload


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title", "file"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-950 shadow-sm outline-none transition focus:border-primary-600 focus:ring-4 focus:ring-blue-100",
                    "placeholder": "e.g. Lease Agreement Review",
                }
            ),
            "file": forms.ClearableFileInput(
                attrs={
                    "class": "w-full rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-6 text-sm text-slate-600 shadow-sm transition file:mr-4 file:rounded-lg file:border-0 file:bg-primary-600 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white hover:border-primary-200 hover:bg-blue-50",
                    "accept": "application/pdf,.pdf",
                }
            ),
        }

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        validate_pdf_upload(uploaded_file)
        return uploaded_file

    @staticmethod
    def safe_original_filename(uploaded_file):
        return get_valid_filename(Path(uploaded_file.name).name)
