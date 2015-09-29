import inspect
import typing


class view_args(object):

    def __init__(self, *args, **settings):
        self.func = args[0]
        self.full_arg_spec = inspect.getfullargspec(self.func)
        self.annotations = self.full_arg_spec[6] 
        self.requestonly = settings.get('requestonly', True)

    def __call__(self, context, request):
        args = [(arg, None) for arg in self.full_arg_spec[0]]

        # fill default value
        defaults = self.full_arg_spec[3]
        if defaults is not None:
            default_first_index = len(args) - len(defaults)
            for i, default in enumerate(defaults):
                args[default_first_index + i] = (
                    args[default_first_index + i][0], default)

        if request.matchdict:
            self._fill_value_by_source(args, request.matchdict)
        if request.GET:
            self._fill_value_by_source(args, request.GET)
        if request.POST:
            self._fill_value_by_source(args, request.POST)
        if request.content_type == 'application/json':
            self._fill_value_by_source(args, request.json_body)

        args = [arg[1] for arg in args]
        return self.func(request, *args[1:])

    def _fill_value_by_source(self, args, source):
        for i, arg_tuple in enumerate(args):
            key = arg_tuple[0]
            if key in source:
                args[i] = (key, source.get(key))

    def _cast_if_needed(self, key, value):
        if key in self.annotations:
            return typing.cast(self.annotations[key], value)
        else:
            return value
