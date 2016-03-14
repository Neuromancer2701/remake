#!/usr/bin/env python

import sys
import pymake.parser

root_path ='/home/countzero/work/WCS/arm/'

slash = '/'
make_path = list()
make_path.append('')
maketabF = 'make\t-f '
makespaceF = 'make -f '
_make = 'make'
make_file = 'Makefile'
_cd = 'cd '
_semi = ';'
source_dirs = 'SRCDIRS'
cxx_flags = 'EXTRA_CFLAGS'
srcfiles = 'SRCS'
libfiles = 'LIB_FLAGS'
libfiles2 = 'INLIBS'
dependancies = 'DEP_LIBS'
target   = 'TARGET'

attributies = {cxx_flags, srcfiles, libfiles, libfiles2, dependancies, target}

make_files_tree = list()

for f in make_path:
    if "Make" not in f:
        total_path = root_path + f + make_file
    else:
        total_path = root_path + f

    print "Parsing %s" % total_path
    fd = open(total_path, 'rU')
    s = fd.read()
    fd.close()
    statments = pymake.parser.parsestring(s, total_path)

    folder  = ''
    file = ''

    make_file_dic = dict()
    make_file_dic['name'] = total_path


    for statment in statments:
        folder  = ''
        file = ''
        if hasattr(statment, 'vnameexp'):
            if statment.vnameexp.s == source_dirs:
                for dir in statment.value.split():
                    make_path.append(f + dir + slash)

            elif statment.vnameexp.s in attributies:
                if statment.vnameexp.s in make_file_dic:
                    make_file_dic[statment.vnameexp.s].extend(statment.value.split())
                else:
                    make_file_dic[statment.vnameexp.s] = statment.value.split()


        elif  hasattr(statment, 'exp'):
            if hasattr(statment.exp, 's'):
                if 'rm' in statment.exp.s or '#' in statment.exp.s:
                    continue
                cd   = statment.exp.s.find(_cd)
                semi = statment.exp.s.find(_semi)
                if cd >= 0 and semi >= 0:
                    folder  = statment.exp.s[cd + len(_cd): semi]
                make_f = statment.exp.s.find(maketabF)
                semi = statment.exp.s.find(_semi)
                if make_f >= 0:
                    file = statment.exp.s[make_f + len(maketabF):]
                else:
                    make_f = statment.exp.s.find(makespaceF)
                    if make_f >= 0:
                        file = statment.exp.s[make_f + len(makespaceF):]
                        file_list = file.split()
                        file = file_list[0]

                file = file.rstrip(_semi)  # remove trail ; if found

                if len(folder) > 0 and len(file) > 0:
                    if f + folder + slash + file not in make_path:
                        make_path.append(f + folder + slash + file)
                elif len(folder) > 0 and statment.exp.s.find(_make) >  0:
                    if f + folder not in make_path:
                        make_path.append(f + folder + slash)
                else:
                    if len(file) > 0:
                        if f + file not in make_path:
                            make_path.append(f + file)
    make_files_tree.append(make_file_dic)

print "Size of Make Path %d" % len(make_path)
print "Size of Make files tree %d" % len(make_files_tree)


import json
with open('makefiletree.json', 'w') as fp:
    json.dump(make_files_tree, fp)

