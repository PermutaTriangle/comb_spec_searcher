from coincidence_classification import *
from util import *

coincidence_classification = {
    Perm((0, 1, 2)) : coincclass012,
    Perm((0, 2, 1)) : coincclass021,
    Perm((1, 0, 2)) : coincclass102,
    Perm((1, 2, 0)) : coincclass120,
    Perm((2, 0, 1)) : coincclass201,
    Perm((2, 1, 0)) : coincclass210
}

basisisi = [
    "0132_0213_0231_0312_0321_1032_1302_1320_2031_2301_3021_3120",
    "0123_0132_0213_0231_0312_1023_1203_1230_2013_2301_3012",
    "0132_0213_0231_0312_0321_1032_1302_1320_2031_2301_3021",
    "0132_0213_0231_0312_0321_1032_1302_1320_2031_2301_3120",
    "0132_0213_0231_0312_0321_1032_1302_1320_2031_3021_3120",
    "0132_0213_0231_0312_0321_1032_1302_1320_2301_3021_3120",
    "0132_0213_0231_0312_0321_1302_1320_2031_2301_3021_3120",
    "0132_0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
    "0132_0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
    "0132_0231_0312_0321_1032_1302_1320_2031_2301_3021_3120",
    "0213_0231_0312_0321_1032_1302_1320_2031_2301_3021_3120"
]

final_res = list()

for b in basisisi:
    print(b, file=sys.stderr)
    maxbin = count_maximal_binary_patterns(task_to_basis(b), coincidence_classification)
    maxbinc = count_maximal_binary_patterns_from_classical_class(task_to_basis(b), coincidence_classification)
    print("Total {}: {} {}".format(b, maxbin, maxbinc), file=sys.stderr)
    final_res.append((b, maxbin, maxbinc))

for (b, maxbin, maxbinc) in final_res:
    print("{}: {} {}".format(b, maxbin, maxbinc))
