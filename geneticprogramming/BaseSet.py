class Baseset(object):
    """
    Basic list of primitive functions granted to the problem
    """

    def __init__(self):
        # collection of primitives
        self.primitives = []
        # collection of available ephemeral routines
        self.ephemerals = []
        # dict of instantiated ephemerals
        self.ephemeral_instances = {}
        # collection of terminals
        self.terminals = []

    def add_primitive(self, primitive, in_types, ret_type, name=None):
        """
        Same as for DEAPs PrimitiveSetTyped
        """
        self.primitives.append((primitive, in_types, ret_type, name))

    def add_terminal(self, terminal, ret_type, name=None):
        """
        Same as for DEAPs PrimitiveSetTyped
        """
        self.terminals.append((terminal, ret_type, name))

    def add_ephemeral(self, name, ephemeral, ret_type):
        """
        Same as for DEAPs PrimitiveSetTyped
        """
        self.ephemerals.append((name, ephemeral, ret_type))

    def get_ephemeral_instance(self, idx):
        """creates a new ephemeral and stores it and returns it
        :param idx: the id of the ephemeral to instantiate
        """
        (name, func, ret) = self.ephemerals[idx]
        name = 'E%s' % len(self.ephemeral_instances)
        value = func()
        self.ephemeral_instances[name] = value
        return name, value
