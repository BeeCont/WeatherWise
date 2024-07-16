class BaseLocation:
    def get_coordinates(self):
        raise NotImplementedError("Subclasses should implement this method")