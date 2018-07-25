
class Singleton(type):
    """
    Singleton metadata class. It allows only one instance per class.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def get_instance(cls):
        """
        Returns the saved instance.
        :return: The single copy of the object instance. A new object is created if it has not been instantiated yet.
        """
        return cls._instances[cls] if cls in cls._instances.keys() else cls()
