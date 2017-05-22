def get_line_number(line):
    return int(line.split(':')[0].replace('L', ''))

def compress_linenumbers(linelist):
    first_number = get_line_number(linelist[0])
    for idx, line in enumerate(linelist):
        linelist[idx] = 'L' + str(first_number + idx) + ':' + line.split(':')[1]
    last_number = get_line_number(linelist[-1])
    return linelist, last_number

def get_key_listing(uuid, var, last_number, class_name):
    new_numbers = [last_number + idx + 1 for idx in range(3)]
    new_numbers.reverse()
    return [
        "L{0}:    ldc '{1}' \n".format(new_numbers.pop(), uuid.lower()),
        "L{0}:    invokestatic Method java/util/UUID fromString (Ljava/lang/String;)Ljava/util/UUID; \n".format(new_numbers.pop()),
        "L{0}:    putstatic Field com/bitwig/flt/packaging/core/{1} {2} Ljava/util/UUID; \n".format(new_numbers.pop(), class_name, var)
    ]

def get_rec_listing(uuid, filename, last_number, class_name, hashmap_name):
    new_numbers = [last_number + idx + 1 for idx in range(6)]
    new_numbers.reverse()
    return [
        "L{0}:  getstatic Field com/bitwig/flt/packaging/core/{1} {2} Ljava/util/Map; \n".format(new_numbers.pop(), class_name, hashmap_name),
        "L{0}:  ldc '{1}' \n".format(new_numbers.pop(), uuid.lower()),
        "L{0}:  invokestatic Method java/util/UUID fromString (Ljava/lang/String;)Ljava/util/UUID; \n".format(new_numbers.pop()),
        "L{0}:  ldc '{1}' \n".format(new_numbers.pop(), filename),
        "L{0}:  invokeinterface InterfaceMethod java/util/Map put (Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object; 3 \n".format(new_numbers.pop()),
        "L{0}:  pop \n".format(new_numbers.pop())
    ]

def remove_last_linenumbertable(linelist):
    for idx, line in enumerate(linelist):
        if '.linenumbertable' in line:
            LNT_START = idx
        if '.end linenumbertable' in line:
            LNT_END = idx
    return linelist[:LNT_START + 1] + linelist[LNT_END:]
