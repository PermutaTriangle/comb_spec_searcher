"A strategy for placing a pattern that is binary under the given basis."

import sys
from permuta import *
from grids import Tiling, PositiveClass, Block
from .batch_class import BatchStrategy
from atrapv2.strategies import Strategy
from itertools import chain
from .util import *

# The coincidence class of the classical pattern 012
coincidence_classification = {
        Perm((0, 1, 2)) : [0, 1, 2, 3, 16, 17, 32, 33, 34, 35, 48, 49, 64, 65,
            66, 67, 80, 81, 96, 97, 98, 99, 112, 113, 512, 513, 514, 515, 528,
            529, 544, 545, 546, 547, 560, 561, 1024, 1025, 1026, 1027, 1040,
            1041, 1056, 1057, 1058, 1059, 1072, 1073, 1088, 1089, 1090, 1091,
            1104, 1105, 1120, 1121, 1122, 1123, 1136, 1137, 1536, 1537, 1538,
            1539, 1552, 1553, 1568, 1569, 1570, 1571, 1584, 1585, 2048, 2049,
            2050, 2051, 2064, 2065, 2080, 2081, 2082, 2083, 2096, 2097, 2112,
            2113, 2114, 2115, 2128, 2129, 2144, 2145, 2146, 2147, 2160, 2161,
            2560, 2561, 2562, 2563, 2576, 2577, 2592, 2593, 2594, 2595, 2608,
            2609, 3072, 3073, 3074, 3075, 3088, 3089, 3104, 3105, 3106, 3107,
            3120, 3121, 3136, 3137, 3138, 3139, 3152, 3153, 3168, 3169, 3170,
            3171, 3184, 3185, 3584, 3585, 3586, 3587, 3600, 3601, 3616, 3617,
            3618, 3619, 3632, 3633, 16384, 16385, 16386, 16387, 16400, 16401,
            16416, 16417, 16418, 16419, 16432, 16433, 16448, 16449, 16450,
            16451, 16464, 16465, 16480, 16481, 16482, 16483, 16496, 16497,
            16896, 16897, 16898, 16899, 16912, 16913, 16928, 16929, 16930,
            16931, 16944, 16945, 17408, 17409, 17410, 17411, 17424, 17425,
            17440, 17441, 17442, 17443, 17456, 17457, 17472, 17473, 17474,
            17475, 17488, 17489, 17504, 17505, 17506, 17507, 17520, 17521,
            17920, 17921, 17922, 17923, 17936, 17937, 17952, 17953, 17954,
            17955, 17968, 17969, 32768, 32769, 32770, 32771, 32784, 32785,
            32800, 32801, 32802, 32803, 32816, 32817, 32832, 32833, 32834,
            32835, 32848, 32849, 32864, 32865, 32866, 32867, 32880, 32881,
            33280, 33281, 33282, 33283, 33296, 33297, 33312, 33313, 33314,
            33315, 33328, 33329, 33792, 33793, 33794, 33795, 33808, 33809,
            33824, 33826, 33840, 33856, 33857, 33858, 33859, 33872, 33873,
            33888, 33890, 33904, 34304, 34305, 34306, 34307, 34320, 34321,
            34336, 34338, 34352, 34816, 34817, 34818, 34819, 34832, 34833,
            34848, 34849, 34850, 34851, 34864, 34865, 34880, 34881, 34882,
            34883, 34896, 34897, 34912, 34913, 34914, 34915, 34928, 34929,
            35328, 35329, 35330, 35331, 35344, 35345, 35360, 35361, 35362,
            35363, 35376, 35377, 35840, 35841, 35842, 35843, 35856, 35857,
            35872, 35874, 35888, 35904, 35905, 35906, 35907, 35920, 35921,
            35936, 35938, 35952, 36352, 36353, 36354, 36355, 36368, 36369,
            36384, 36386, 36400, 49152, 49153, 49154, 49155, 49168, 49169,
            49184, 49185, 49186, 49187, 49200, 49201, 49216, 49217, 49218,
            49219, 49232, 49233, 49248, 49249, 49250, 49251, 49264, 49265,
            49664, 49665, 49666, 49667, 49680, 49681, 49696, 49697, 49698,
            49699, 49712, 49713, 50176, 50177, 50178, 50179, 50192, 50193,
            50208, 50210, 50224, 50240, 50241, 50242, 50243, 50256, 50257,
            50272, 50274, 50288, 50688, 50689, 50690, 50691, 50704, 50705,
            50720, 50722, 50736],

    Perm((0, 2, 1)) : [0, 1, 2, 3, 16, 17, 32, 34, 48, 64, 65, 66, 67, 80, 81,
        96, 98, 112, 128, 129, 130, 131, 144, 145, 160, 162, 176, 192, 193,
        194, 195, 208, 209, 224, 226, 240, 512, 513, 514, 515, 528, 529, 544,
        546, 560, 576, 577, 578, 579, 592, 593, 608, 610, 624, 640, 641, 642,
        643, 656, 657, 672, 674, 688, 704, 705, 706, 707, 720, 721, 736, 738,
        752, 1024, 1025, 1026, 1027, 1040, 1041, 1056, 1058, 1072, 1088, 1089,
        1090, 1091, 1104, 1105, 1120, 1122, 1136, 1152, 1153, 1154, 1155, 1168,
        1169, 1184, 1186, 1200, 1216, 1217, 1218, 1219, 1232, 1233, 1248, 1250,
        1264, 1536, 1537, 1538, 1539, 1552, 1553, 1568, 1570, 1584, 1600, 1601,
        1602, 1603, 1616, 1617, 1632, 1634, 1648, 1664, 1665, 1666, 1667, 1680,
        1681, 1696, 1698, 1712, 1728, 1729, 1730, 1731, 1744, 1745, 1760, 1762,
        1776, 2048, 2049, 2050, 2051, 2064, 2065, 2080, 2082, 2096, 2176, 2177,
        2178, 2179, 2192, 2193, 2208, 2210, 2224, 2560, 2561, 2562, 2563, 2576,
        2577, 2592, 2594, 2608, 2688, 2689, 2690, 2691, 2704, 2705, 2720, 2722,
        2736, 3072, 3073, 3074, 3075, 3088, 3089, 3104, 3106, 3120, 3200, 3201,
        3202, 3203, 3216, 3217, 3232, 3234, 3248, 3584, 3585, 3586, 3587, 3600,
        3601, 3616, 3618, 3632, 3712, 3713, 3714, 3715, 3728, 3729, 3744, 3746,
        3760, 8192, 8193, 8194, 8195, 8208, 8209, 8224, 8226, 8240, 8256, 8257,
        8258, 8259, 8272, 8273, 8288, 8290, 8304, 8320, 8321, 8322, 8323, 8336,
        8337, 8352, 8354, 8368, 8384, 8385, 8386, 8387, 8400, 8401, 8416, 8418,
        8432, 8704, 8705, 8706, 8707, 8720, 8721, 8736, 8738, 8752, 8768, 8769,
        8770, 8771, 8784, 8785, 8800, 8802, 8816, 8832, 8833, 8834, 8835, 8848,
        8849, 8864, 8866, 8880, 8896, 8897, 8898, 8899, 8912, 8913, 8928, 8930,
        8944, 9216, 9217, 9218, 9219, 9232, 9233, 9248, 9250, 9264, 9280, 9281,
        9282, 9283, 9296, 9297, 9312, 9314, 9328, 9728, 9729, 9730, 9731, 9744,
        9745, 9760, 9762, 9776, 9792, 9793, 9794, 9795, 9808, 9809, 9824, 9826,
        9840, 10240, 10241, 10242, 10243, 10256, 10257, 10272, 10274, 10288,
        10368, 10369, 10370, 10371, 10384, 10385, 10400, 10402, 10416, 10752,
        10753, 10754, 10755, 10768, 10769, 10784, 10786, 10800, 10880, 10881,
        10882, 10883, 10896, 10897, 10912, 10914, 10928, 11264, 11265, 11266,
        11267, 11280, 11281, 11296, 11298, 11312, 11776, 11777, 11778, 11779,
        11792, 11793, 11808, 11810, 11824, 16384, 16385, 16386, 16387, 16400,
        16401, 16416, 16418, 16432, 16448, 16449, 16450, 16451, 16464, 16465,
        16480, 16482, 16496, 16512, 16513, 16514, 16515, 16528, 16529, 16544,
        16546, 16560, 16576, 16577, 16578, 16579, 16592, 16593, 16608, 16610,
        16624, 17408, 17409, 17410, 17411, 17424, 17425, 17440, 17442, 17456,
        17472, 17473, 17474, 17475, 17488, 17489, 17504, 17506, 17520, 17536,
        17537, 17538, 17539, 17552, 17553, 17568, 17570, 17584, 17600, 17601,
        17602, 17603, 17616, 17617, 17632, 17634, 17648, 18432, 18433, 18434,
        18435, 18448, 18449, 18464, 18466, 18480, 18560, 18561, 18562, 18563,
        18576, 18577, 18592, 18594, 18608, 19456, 19457, 19458, 19459, 19472,
        19473, 19488, 19490, 19504, 19584, 19585, 19586, 19587, 19600, 19601,
        19616, 19618, 19632, 24576, 24577, 24578, 24579, 24592, 24593, 24608,
        24610, 24624, 24640, 24641, 24642, 24643, 24656, 24657, 24672, 24674,
        24688, 24704, 24705, 24706, 24707, 24720, 24721, 24736, 24738, 24752,
        24768, 24769, 24770, 24771, 24784, 24785, 24800, 24802, 24816, 25600,
        25601, 25602, 25603, 25616, 25617, 25632, 25634, 25648, 25664, 25665,
        25666, 25667, 25680, 25681, 25696, 25698, 25712, 26624, 26625, 26626,
        26627, 26640, 26641, 26656, 26658, 26672, 26752, 26753, 26754, 26755,
        26768, 26769, 26784, 26786, 26800, 27648, 27649, 27650, 27651, 27664,
        27665, 27680, 27682, 27696]}

def binary_pattern_classical_class(tiling, basis, **kwargs):
    """Produces a binary pattern strategy from a tiling containing a single
    block of PositiveClass.

    Searches through the coincidence class of the classical patterns of up to
    length k, which is given as a keyword argument. Takes the maximal ones and
    places them in the grid.

    Currently only the classical patterns 012 and 021 are considered.
    """
    if tiling.dimensions.i != 1 or tiling.dimensions.j != 1:
        return

    block = tiling[(0, 0)]
    # Should be k = kwargs.get('k') for the general case
    k = 3
    if isinstance(block, PositiveClass) and k:
        for patt in PermSet.avoiding(basis).of_length(k):
            if patt != Perm((0, 1, 2)):
                continue
            cclass = list(map(lambda m: MeshPatt.unrank(patt, m), coincidence_classification[patt]))
            maximal = list()
            last = None

            for cur in sorted(cclass):
                if cur == last:
                    continue
                add = True
                for other in cclass:
                    if cur < other:
                        add = False
                if add:
                    maximal.append(cur)
                last = cur

            maxibin = filter(lambda x: is_binary(x, basis), maximal)

            # When printing out, the lazy iterator has to materialized
            # maxibin = list(filter(lambda x: is_binary(x, basis), maximal))
            # print("Length of maximal: ", len(maxibin), file=sys.stderr)

            for mpatt in maxibin:
                # print(mpatt, file=sys.stderr)
                # print(None, file=sys.stderr)
                # print(tiling_from_mesh_pattern(mpatt, block.perm_class), file=sys.stderr)
                # print(patt, file=sys.stderr)
                tilings = [Tiling({(0, 0): PositiveClass(PermSet.avoiding(basis + (patt,)))}),
                        tiling_from_mesh_pattern(mpatt, block.perm_class)]
                yield Strategy(("Placing the binary pattern "
                                     "{}").format(mpatt.latex()), tilings, [False, True])
                break
            break
