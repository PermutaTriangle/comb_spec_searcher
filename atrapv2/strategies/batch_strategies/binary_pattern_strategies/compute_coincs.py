from coincidence_classification import coincclass012 as cc012
from coincidence_classification import coincclass021 as cc021
from util import *

import sys

f210 = open("coincidence_classification/coincidence_classification_210.py", "w")

f120 = open("coincidence_classification/coincidence_classification_120.py", "w")
f201 = open("coincidence_classification/coincidence_classification_201.py", "w")
f102 = open("coincidence_classification/coincidence_classification_102.py", "w")

def close_files():
    f210.close()
    f201.close()
    f120.close()
    f102.close()

f210.write("coincidence_class = [\n")

for cclass in cc012:
    f210.write("    " + str(sorted(flip_binshad_vertical(p, 4) for p in cclass)) + ',\n')
    # if not all(flip_binshad_vertical(p, 4) == MeshPatt.unrank(Perm((0,1,2)), p).reverse().rank() for p in cclass):
        # print([MeshPatt.unrank(Perm((2,1,0)), flip_binshad_vertical(p, 4)) for p in cclass])
        # print([MeshPatt.unrank(Perm((0,1,2)), p).reverse() for p in cclass])
        # close_files()
        # sys.exit(0)

f210.write("]\n")

f201.write("coincidence_class = [\n")
f120.write("coincidence_class = [\n")
f102.write("coincidence_class = [\n")

for cclass in cc021:
    f201.write("    " + str(sorted(flip_binshad_horizontal(p, 4) for p in cclass)) + ',\n')
    f120.write("    " + str(sorted(flip_binshad_vertical(p, 4) for p in cclass)) + ',\n')
    f102.write("    " + str(sorted(flip_binshad_horizontal(flip_binshad_vertical(p, 4), 4) for p in cclass)) + ',\n')
    # if not all(flip_binshad_horizontal(p, 4) == MeshPatt.unrank(Perm((0,1,2)), p).complement().rank() for p in cclass):
        # print([MeshPatt.unrank(Perm((2,1,0)), flip_binshad_horizontal(p, 4)) for p in cclass])
        # print([MeshPatt.unrank(Perm((0,1,2)), p).complement() for p in cclass])
        # break
        # close_files()
        # sys.exit(0)

f201.write(']\n')
f120.write(']\n')
f102.write(']\n')

close_files()
