def get_existing_field_values(request, fields):
    if request.method == 'POST':
        return map(lambda f: (f[0], f[1], request.POST.get(f[1], '')), fields)
    else:
        return fields

