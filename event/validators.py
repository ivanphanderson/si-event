def validate_event_employee_fields(role_name, pph, honor, idx):
  if role_name == '':
    role_name = f'Role_{idx}'
  if honor == '':
    honor = 0
  if pph == '':
    pph = 0
  if int(pph) < 0 or int(honor) < 0:
    return role_name, abs(int(pph)), abs(int(honor))
  return role_name, int(pph), int(honor)