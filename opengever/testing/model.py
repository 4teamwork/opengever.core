class TransparentModelLoader(object):
    """Mixin class to transparently load model instances for a ModelContainer.

    Hooks into a builders before_create to load the model instances for all
    arguments specified in model_arguments.

    """
    auto_loaded_models = tuple()

    def before_create(self):
        for attribute_name in self.auto_loaded_models:
            maybe_model = self.arguments.get(attribute_name)
            if maybe_model and hasattr(maybe_model, 'load_model'):
                model = maybe_model.load_model()
                self.arguments[attribute_name] = model

        super(TransparentModelLoader, self).before_create()
