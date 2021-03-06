from common.entity.entities import Node, Type 

def dump_node(node):
    """
    This function returns a dictionary representation of a node 
    or a list of dictionaries representig various node.
    :param node: a Node or a List os Nodes
    """
    if node == None:
        return None
    if type(node) == Node:
        k, n, t = node.to_dict()
        n['type'] = t
        return n
    elif type(node) == list:
        res = []
        for n in node:
            if type(n) == Node:
                res.append(dump_node(n))
        return res
    else:
        return None

def dump_type(_type):
    """
    This function returns a dictionary representation of a type 
    or a list of dictionaries representig various types.
    :param node: a Type or a List os Type
    """
    if _type == None:
        return None
    if type(_type) == Type:
        k, t = _type.to_dict()
        return t
    elif type(_type) == list:
        res = []
        for t in _type:
            if type(_type) == Type:
                res.append(dump_type(t))
        return res
    else:
        return None
 