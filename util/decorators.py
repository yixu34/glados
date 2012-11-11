from django.utils.decorators import available_attrs
from functools import wraps
from util.responses import ApiError

def param_required(params):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not isinstance(params, list):
                to_check = [params]
            else:
                to_check = params
            for param in to_check:
                p = request.POST.get(param, None)
                if not p:
                    return ApiError('Missing required param: %s' % param)
                kwargs[param] = p
            return view_func(request, *args, **kwargs)
        return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)
    return decorator

