from django.core.exceptions import ValidationError

def validate_event_employee_fields(pph, honor):
  if pph < 0 or honor < 0:
    raise ValidationError('PPH atau Honor tidak boleh negatif')