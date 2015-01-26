
def attr_name(key):
    return key.strip().replace('#EXT-X-','').replace('-','_').lower()

def my_bool(a):
    if a.strip().lower()=='no':
        return False
    elif a.strip().lower()=='yes':
        return True
    raise ValueError

def my_dict(a):
    a = list(my_split(a))
    dct = {}
    for b in a:
        key,val = b.split('=')
        key = attr_name(key)
        dct[key] = my_cast(val)
    return dct

def my_list(a):
    if not ',' in a:
        raise ValueError
    l = list(my_split(a))
    if len(l)>=1:  # TODO think about this
        return [my_cast(x.strip('\'\"')) for x in l]

def my_split(string,sep=','):
    start = 0
    end = 0
    inString = False
    while end < len(string):
        if string[end] not in sep or inString: # mid string
            if string[end] in '\'\"':
                inString = not inString
            end +=1
        else: # separator
            yield string[start:end]
            end +=1
            start = end
    if start != end:# ignore empty items
        yield string[start:end]


def my_cast(val):
    if type(val) in (int, bool, float, list, dict):
        return val

    # intelligent casting sort of
    try:
        return int(val)
    except ValueError:
        pass

    try:
        return float(val)
    except ValueError:
        pass

    try:
        return my_bool(val)
    except ValueError:
        pass

    try:
        return my_dict(val)
    except ValueError:
        pass

    try:
        return my_list(val)
    except ValueError:
        pass

    return val

