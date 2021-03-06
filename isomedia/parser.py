import os

from isomedia import atom
from isomedia.atom import Atom, ContainerAtom, RootAtom
from isomedia.atom import interpret_atom_header, interpret_int32

def need_read(ptr, n):
    data = ptr.read(n)
    if data is None or len(data) != n:
        raise EOFError
    return data

def parse_file(ptr):
    root = RootAtom()

    current_offset = 0
    while True:
        try:
            new_atom, atom_size = parse_atom(ptr, parent=None, offset=current_offset)
            root.children.append(new_atom)
            current_offset += atom_size
        except EOFError:
            break

    return root

def parse_atom(ptr, parent=None, offset=None):
    def parse_atom_header(ptr):
        data = need_read(ptr, 8)
        atom_size = interpret_int32(data, 0)
        if atom_size == 1:
            data += need_read(ptr, 8)

        return data

    atom_header = parse_atom_header(ptr)
    atom_type, atom_size, header_length = interpret_atom_header(atom_header)
    atom_body_length = atom_size - header_length

    if atom_type in atom.CONTAINER_ATOMS:
        new_atom = ContainerAtom(atom_header, parent, offset)
        new_atom.children = parse_children(ptr, atom_size - header_length, parent=new_atom, offset=offset + header_length)
    elif atom_type in atom.ATOM_TYPE_TO_CLASS:
        new_atom_class = atom.ATOM_TYPE_TO_CLASS[atom_type]
        if new_atom_class.LOAD_DATA:
            atom_body = need_read(ptr, atom_body_length)
        else:
            atom_body = ''
            ptr.seek(atom_body_length, os.SEEK_CUR)

        atom_data = atom_header + atom_body
        new_atom = new_atom_class(atom_data, parent, offset)
    else:
        atom_body = need_read(ptr, atom_size - header_length)
        atom_data = atom_header + atom_body
        new_atom = Atom(atom_data, parent, offset)

    return (new_atom, atom_size)

def parse_children(ptr, total_bytes, parent=None, offset=None):
    children = []
    bytes_read = 0

    while bytes_read < total_bytes:
        new_atom, atom_size = parse_atom(ptr, parent=parent, offset=offset + bytes_read)
        children.append(new_atom)
        bytes_read += atom_size

    if bytes_read != total_bytes:
        raise Exception

    return children
