import numpy as np
from scipy.interpolate import interp2d
from scipy.interpolate import interp1d
from os.path import basename


class CompleteDcm:

    def __init__(self):
        self.header = []
        self.functions = []
        self.label = []
        self.rest = []
        self.name = ''

    def alllabelnames(self):
        all_names = []
        for a_label in self.label:
            all_names.append(a_label.name)
        return all_names

    def labelindcm(self, label_name):
        all_names = self.alllabelnames()
        for a_label in all_names:
            if a_label == label_name:
                return True
        return False

    def labeltyp(self, label_name):
        for a_label in self.label:
            if a_label.name == label_name:
                return a_label.typ.name
        return False

    def labelposition(self, label_name):
        for a_label in self.label:
            if a_label.name == label_name:
                return self.label.index(a_label)

    def addlabel(self, new_label):
        if not self.labelindcm(new_label.name):
            self.label.append(new_label)
            return True
        return False

    def dellabel(self, label_name):
        if self.labelindcm(label_name):
            position = self.labelposition(label_name)
            if position:
                self.label.remove(self.label[position])
                return True
        return False

    def getlabel(self, label_name):
        if self.labelindcm(label_name):
            position = self.labelposition(label_name)
            return self.label[position]

    def multigetlabel(self, label_list):
        return_label = []
        for label_name in label_list:
            temp_label = self.getlabel(label_name)
            if temp_label:
                return_label.append(temp_label)
        return return_label

    def multidellabel(self, label_list):
        return_boolean = []
        for label_name in label_list:
            return_boolean.append(self.dellabel(label_name))
        return return_boolean

    def copy(self):
        dcm_copy = CompleteDcm()
        dcm_copy.label = list(self.label)
        dcm_copy.functions = list(self.functions)
        dcm_copy.header = list(self.header)
        dcm_copy.rest = list(self.rest)

    def copylabel(self, label_name):
        lbl = self.getlabel(label_name)
        label_copy = DcmFormat(lbl.typ.name)
        label_copy.name = str(lbl.name)
        label_copy.funktion = str(lbl.name)
        label_copy.langname = str(lbl.langname)
        label_copy.typ = lbl.typ.copy()
        return label_copy

    def interpolate(self, label_name, x, y=[0]):
        lbl_copy = self.copylabel(label_name)
        if lbl_copy.typ.name == 'MAP':
            grid_x = np.array(lbl_copy.typ.x_axis)
            grid_y = np.array(lbl_copy.typ.y_axis)
            values = np.array(lbl_copy.typ.values).reshape((len(grid_y), len(grid_x)))
            new_x = np.array(x)
            new_y = np.array(y)
            interp_fun = interp2d(grid_x, grid_y, values, kind='linear')
            interp_data = interp_fun(new_x, new_y)
            new_values = interp_data.flatten()
            return_values = new_values.tolist()
            lbl_copy.typ.x_axis = list(x)
            lbl_copy.typ.y_axis = list(y)
            lbl_copy.typ.values = return_values
            return lbl_copy

        if lbl_copy.typ.name == 'CUR':
            grid_x = np.array(lbl_copy.typ.x_axis)
            grid_y = np.array([1])
            values = np.array(lbl_copy.typ.values).reshape((1, len(grid_x)))
            new_x = np.array(x)
            new_y = np.array([1])
            interp_fun = interp2d(grid_x, grid_y, values, kind='linear')
            interp_data = interp_fun(new_x, new_y)
            new_values = interp_data.flatten()
            return_values = new_values.tolist()
            lbl_copy.typ.x_axis = list(x)
            lbl_copy.typ.values = return_values
            return lbl_copy

    def nd_interpolate(self, label_name, x, y=[0]):
        lbl_copy = self.copylabel(label_name)
        if lbl_copy.typ.name == 'MAP':
            grid_x = np.array(lbl_copy.typ.x_axis)
            grid_y = np.array(lbl_copy.typ.y_axis)
            values = np.array(lbl_copy.typ.values).reshape((len(grid_y), len(grid_x)))
            new_x = np.array(x)
            new_y = np.array(y)
            interp_fun = interp2d(grid_x, grid_y, values, kind='linear')
            interp_data = interp_fun(new_x, new_y)

            return interp_data

        if lbl_copy.typ.name == 'CUR':
            grid_x = np.array(lbl_copy.typ.x_axis)
            grid_y = np.array([0, 1, 2])
            val = lbl_copy.typ.values
            values = np.array([val, val, val])
            new_x = np.array(x)
            new_y = np.array([1])
            interp_fun = interp2d(grid_x, grid_y, values, kind='linear')
            interp_data = interp_fun(new_x, new_y)

            return interp_data

    def nd_interp_map_in_cur(self, label_name, x):
        lbl_copy = self.copylabel(label_name)

        grid_x = np.array(lbl_copy.typ.x_axis)
        grid_y = np.array([0, 1, 2])
        val = lbl_copy.typ.values
        values = np.array([val, val, val])
        new_y = np.array([1])
        z = np.array([])
        for single_curve in x:
            for value in single_curve:
                new_x = np.array(value)
                interp_fun = interp2d(grid_x, grid_y, values, kind='linear')
                z = np.append(z, interp_fun(new_x, new_y))

        z = np.array(z).reshape(x.shape)

        return z


class DcmFormat:

    def __init__(self, typ):
        self.name = ''
        self.langname = ''
        self.funktion = ''
        if typ == 'MAP':
            self.typ = TypMap()
        elif typ == 'CUR':
            self.typ = TypCurve()
        elif typ == 'C':
            self.typ = TypConstant()
        elif typ == 'CA':
            self.typ = TypConstArray()

    def gettyp(self):
        if self.typ.name == 'MAP':
            return 'MAP'
        if self.typ.name == 'CUR':
            return 'CUR'
        if self.typ.name == 'C':
            return 'C'
        if self.typ.name == 'CA':
            return 'CA'

    def copy(self):
        label_copy = DcmFormat(self.typ.name)
        label_copy.name = str(self.name)
        label_copy.funktion = str(self.name)
        label_copy.langname = str(self.langname)
        label_copy.typ = self.typ.copy()
        return label_copy


class TypMap:

    def __init__(self):
        self.name = 'MAP'
        self.x_axis = []
        self.y_axis = []
        self.values = []
        self.x_unit = ''
        self.y_unit = ''
        self.w_unit = ''
        self.x_count = ''
        self.y_count = ''

    def copy(self):
        map_copy = TypMap()
        map_copy.name = str(self.name)
        map_copy.x_axis = list(self.x_axis)
        map_copy.y_axis = list(self.y_axis)
        map_copy.values = list(self.values)
        map_copy.x_unit = str(self.x_unit)
        map_copy.y_unit = str(self.y_unit)
        map_copy.w_unit = str(self.w_unit)
        map_copy.x_count = str(self.x_count)
        map_copy.y_count = str(self.y_count)
        return map_copy


class TypStrMap:

    def __init__(self):
        self.name = 'strMAP'
        self.x_axis = []
        self.y_axis = []
        self.values = []
        self.x_unit = ''
        self.y_unit = ''
        self.w_unit = ''
        self.x_count = ''
        self.y_count = ''

    def copy(self):
        map_copy = TypStrMap()
        map_copy.name = str(self.name)
        map_copy.x_axis = list(self.x_axis)
        map_copy.y_axis = list(self.y_axis)
        map_copy.values = list(self.values)
        map_copy.x_unit = str(self.x_unit)
        map_copy.y_unit = str(self.y_unit)
        map_copy.w_unit = str(self.w_unit)
        map_copy.x_count = str(self.x_count)
        map_copy.y_count = str(self.y_count)
        return map_copy


class TypCurve:

    def __init__(self):
        self.name = 'CUR'
        self.x_axis = []
        self.values = []
        self.x_unit = ''
        self.w_unit = ''
        self.x_count = ''

    def copy(self):
        cur_copy = TypCurve()
        cur_copy.name = str(self.name)
        cur_copy.x_axis = list(self.x_axis)
        cur_copy.values = list(self.values)
        cur_copy.x_unit = str(self.x_unit)
        cur_copy.w_unit = str(self.w_unit)
        cur_copy.x_count = str(self.x_count)
        return cur_copy


class TypStrCurve:

    def __init__(self):
        self.name = 'strCUR'
        self.x_axis = []
        self.values = []
        self.x_unit = ''
        self.w_unit = ''
        self.x_count = ''

    def copy(self):
        cur_copy = TypStrCurve()
        cur_copy.name = str(self.name)
        cur_copy.x_axis = list(self.x_axis)
        cur_copy.values = list(self.values)
        cur_copy.x_unit = str(self.x_unit)
        cur_copy.w_unit = str(self.w_unit)
        cur_copy.x_count = str(self.x_count)
        return cur_copy


class TypConstant:

    def __init__(self):
        self.name = 'C'
        self.value = []
        self.unit = ''

    def copy(self):
        c_copy = TypConstant()
        c_copy.name = str(self.name)
        c_copy.value = str(self.value)
        c_copy.unit = str(self.unit)
        return c_copy


class TypStrConstant:

    def __init__(self):
        self.name = 'strC'
        self.value = []
        self.unit = ''

    def copy(self):
        c_copy = TypStrConstant()
        c_copy.name = str(self.name)
        c_copy.value = str(self.value)
        c_copy.unit = str(self.unit)
        return c_copy


class TypConstArray:

    def __init__(self):
        self.name = 'CA'
        self.values = []
        self.w_unit = ''
        self.x_count = ''
        self.y_count = ''

    def copy(self):
        ca_copy = TypConstArray()
        ca_copy.name = str(self.name)
        ca_copy.values = list(self.values)
        ca_copy.w_unit = str(self.w_unit)
        ca_copy.x_count = str(self.x_count)
        ca_copy.y_count = str(self.y_count)
        return ca_copy


class TypStrConstArray:

    def __init__(self):
        self.name = 'strCA'
        self.values = []
        self.w_unit = ''
        self.x_count = ''
        self.y_count = ''

    def copy(self):
        ca_copy = TypStrConstArray()
        ca_copy.name = str(self.name)
        ca_copy.values = list(self.values)
        ca_copy.w_unit = str(self.w_unit)
        ca_copy.x_count = str(self.x_count)
        ca_copy.y_count = str(self.y_count)
        return ca_copy


def importdcm(file_path):
    in_header = True
    in_funktionen = False
    in_kennfeld = False
    in_kennlinie = False
    in_constarray = False
    in_constant = False

    complete_dcm = CompleteDcm()
    complete_dcm.name = basename(file_path)
    with open(file_path) as f:
        for line in f:
            if len(line) > 0:
                line = line.rstrip('\n')
                words = line.split()
                if 'END' in words:
                    if in_kennfeld:
                        complete_dcm.label.append(one_map)
                        in_kennfeld = False
                    elif in_constant:
                        complete_dcm.label.append(one_c)
                        in_constant = False
                    elif in_kennlinie:
                        complete_dcm.label.append(one_curve)
                        in_kennlinie = False
                    elif in_constarray:
                        complete_dcm.label.append(one_ca)
                    elif in_funktionen:
                        in_funktionen = False
                    else:
                        complete_dcm.rest.append(line)

                elif 'FUNKTIONEN' in words or in_funktionen:
                    in_header = False
                    if not in_funktionen:
                        in_funktionen = True

                    if 'FKT' in words:
                        complete_dcm.functions.append([words[1], " ".join(words[2:])])

                elif 'FESTWERT' in words or in_constant:
                    in_header = False
                    if not in_constant:
                        in_constant = True
                        one_c = DcmFormat('C')
                        one_c.name = words[1]

                    if 'LANGNAME' in words:
                        one_c.langname = " ".join(words[1:])
                    elif 'EINHEIT_W' in words:
                        one_c.typ.w_unit = " ".join(words[1:])
                    elif 'WERT' in words:
                        one_c.typ.value += (float(i) for i in words[1:])
                    elif 'TEXT' in words:
                        one_c.typ.value = " ".join(words[1:])
                        one_c.typ.name = 'strC'

                elif 'KENNFELD' in words or in_kennfeld:
                    in_header = False
                    if not in_kennfeld:
                        in_kennfeld = True
                        one_map = DcmFormat('MAP')
                        one_map.name = words[1]
                        one_map.typ.x_count = words[2]
                        one_map.typ.y_count = words[3]

                    if 'LANGNAME' in words:
                        one_map.langname = " ".join(words[1:])
                    elif 'FUNKTION' in words:
                        one_map.funktion = words[1]
                    elif 'EINHEIT_X' in words:
                        one_map.typ.x_unit = " ".join(words[1:])
                    elif 'EINHEIT_Y' in words:
                        one_map.typ.y_unit = " ".join(words[1:])
                    elif 'EINHEIT_W' in words:
                        one_map.typ.w_unit = " ".join(words[1:])
                    elif 'ST/X' in words:
                        one_map.typ.x_axis += (float(i) for i in words[1:])
                    elif 'ST/Y' in words:
                        one_map.typ.y_axis += (float(i) for i in words[1:])
                    elif 'ST_TX/X' in words:
                        one_map.typ.x_axis += (str(i) for i in words[1:])
                        if not one_map.typ.name == 'strMAP':
                            one_map.typ.name = 'strMAP'
                    elif 'ST_TX/Y' in words:
                        one_map.typ.y_axis += (str(i) for i in words[1:])
                        if not one_map.typ.name == 'strMAP':
                            one_map.typ.name = 'strMAP'
                    elif 'WERT' in words:
                        one_map.typ.values += (float(i) for i in words[1:])
                    elif 'TEXT' in words:
                        one_map.typ.values += (str(i) for i in words[1:])
                        if not one_map.typ.name == 'strMAP':
                            one_map.typ.name = 'strMAP'
                elif 'GRUPPENKENNFELD' in words or in_kennfeld:
                    in_header = False
                    if not in_kennfeld:
                        in_kennfeld = True
                        one_map = DcmFormat('MAP')
                        one_map.name = words[1]
                        one_map.typ.x_count = words[2]
                        one_map.typ.y_count = words[3]

                    if 'LANGNAME' in words:
                        one_map.langname = " ".join(words[1:])
                    elif 'FUNKTION' in words:
                        one_map.funktion = words[1]
                    elif 'EINHEIT_X' in words:
                        one_map.typ.x_unit = " ".join(words[1:])
                    elif 'EINHEIT_Y' in words:
                        one_map.typ.y_unit = " ".join(words[1:])
                    elif 'EINHEIT_W' in words:
                        one_map.typ.w_unit = " ".join(words[1:])
                    elif 'ST/X' in words:
                        one_map.typ.x_axis += (float(i) for i in words[1:])
                    elif 'ST/Y' in words:
                        one_map.typ.y_axis += (float(i) for i in words[1:])
                    elif 'ST_TX/X' in words:
                        one_map.typ.x_axis += (str(i) for i in words[1:])
                        if not one_map.typ.name == 'strMAP':
                            one_map.typ.name = 'strMAP'
                    elif 'ST_TX/Y' in words:
                        one_map.typ.y_axis += (str(i) for i in words[1:])
                        if not one_map.typ.name == 'strMAP':
                            one_map.typ.name = 'strMAP'
                    elif 'WERT' in words:
                        one_map.typ.values += (float(i) for i in words[1:])
                    elif 'TEXT' in words:
                        one_map.typ.values += (str(i) for i in words[1:])
                        if not one_map.typ.name == 'strMAP':
                            one_map.typ.name = 'strMAP'
                elif 'KENNLINIE' in words or in_kennlinie:
                    in_header = False
                    if not in_kennlinie:
                        in_kennlinie = True
                        one_curve = DcmFormat('CUR')
                        one_curve.name = words[1]
                        one_curve.typ.x_count = words[2]

                    if 'LANGNAME' in words:
                        one_curve.langname = " ".join(words[1:])
                    elif 'FUNKTION' in words:
                        one_curve.funktion = words[1]
                    elif 'EINHEIT_X' in words:
                        one_curve.typ.x_unit = " ".join(words[1:])
                    elif 'EINHEIT_W' in words:
                        one_curve.typ.w_unit = " ".join(words[1:])
                    elif 'ST/X' in words:
                        one_curve.typ.x_axis += (float(i) for i in words[1:])
                    elif 'ST_TX/X' in words:
                        one_curve.typ.x_axis += (str(i) for i in words[1:])
                        if not one_curve.typ.name == 'strCUR':
                            one_curve.typ.name = 'strCUR'
                    elif 'WERT' in words:
                        one_curve.typ.values += (float(i) for i in words[1:])
                    elif 'TEXT' in words:
                        one_curve.typ.values += (str(i) for i in words[1:])
                        if not one_curve.typ.name == 'strCUR':
                            one_curve.typ.name = 'strCUR'

                elif 'FESTWERTEBLOCK' in words or in_constarray:
                    in_header = False
                    if not in_constarray:
                        in_constarray = True
                        one_ca = DcmFormat('CA')
                        one_ca.name = words[1]
                        one_ca.typ.x_count = words[2]
                        if len(words) > 3:
                            one_ca.typ.y_count = words[3]

                    if 'LANGNAME' in words:
                        one_ca.langname = " ".join(words[1:])
                    elif 'EINHEIT_W' in words:
                        one_ca.typ.w_unit = " ".join(words[1:])
                    elif 'WERT' in words:
                        one_ca.typ.values += (float(i) for i in words[1:])
                    elif 'TEXT' in words:
                        one_ca.typ.values += (str(i) for i in words[1:])
                        if not one_ca.typ.name == 'strCA':
                            one_curve.typ.name = 'strCA'

                else:
                    if in_header:
                        complete_dcm.header.append(line)
                    else:
                        if len(words) == 0:
                            if len(complete_dcm.rest) > 0:
                                if not len(complete_dcm.rest[-1]) == 0:
                                    complete_dcm.rest.append(line)
                        else:
                            complete_dcm.rest.append(line)

            elif not in_kennlinie and not in_funktionen and not in_header and not \
                    in_kennfeld and not in_constarray and not in_constant:
                complete_dcm.rest.append(line)

    return complete_dcm


def savedcm(complete_dcm, file_path):
    f = open(file_path, 'w')
    if f:
        dcm = complete_dcm
        nl = '\n'
        for line in dcm.header:
            f.writelines(line + nl)

        f.writelines('FUNKTIONEN' + nl)
        for line in dcm.functions:
            f.write('   FKT ')
            f.writelines(line)
            f.write(nl)

        f.writelines('END' + nl + nl)

        for a_label in dcm.label:
            if a_label.typ.name == 'MAP':
                f.writelines('KENNFELD ' + a_label.name + ' ' + a_label.typ.x_count + ' ' + a_label.typ.y_count + nl)
                f.writelines('   LANGNAME ' + a_label.langname + nl)
                f.writelines('   FUNKTION ' + a_label.funktion + nl)
                f.writelines('   EINHEIT_X ' + a_label.typ.x_unit + nl)
                f.writelines('   EINHEIT_Y ' + a_label.typ.y_unit + nl)
                f.writelines('   EINHEIT_W ' + a_label.typ.w_unit)
                x_loop = 0
                for x_axis in a_label.typ.x_axis:
                    if x_loop == 6:
                        x_loop = 0

                    if x_loop == 0:
                        f.write(nl)
                        f.writelines('   ST/X')

                    f.write('   ' + str(x_axis))
                    x_loop += 1

                w_loop = 0
                w_count = int(a_label.typ.x_count)
                y_loop = 0
                for values in a_label.typ.values:
                    if y_loop == 0 or w_count == int(a_label.typ.x_count):
                        f.writelines(nl + '   ST/Y   ' + str(a_label.typ.y_axis[y_loop]))
                        w_count = 0
                        w_loop = 0
                        y_loop += 1

                    if w_loop == 6:
                        w_loop = 0

                    if w_loop == 0:
                        f.write(nl)
                        f.writelines('   WERT')

                    f.write('   ' + str(values))
                    w_loop += 1
                    w_count += 1

                f.writelines(nl + 'END' + nl + nl)
            if a_label.typ.name == 'CUR':
                f.writelines('KENNLINIE ' + a_label.name + ' ' + a_label.typ.x_count + nl)
                f.writelines('   LANGNAME ' + a_label.langname + nl)
                f.writelines('   FUNKTION ' + a_label.funktion + nl)
                f.writelines('   EINHEIT_X ' + a_label.typ.x_unit + nl)
                f.writelines('   EINHEIT_W ' + a_label.typ.w_unit)
                x_loop = 0
                for x_axis in a_label.typ.x_axis:
                    if x_loop == 6:
                        x_loop = 0

                    if x_loop == 0:
                        f.write(nl)
                        f.writelines('   ST/X')

                    f.write('   ' + str(x_axis))
                    x_loop += 1

                w_loop = 0
                for values in a_label.typ.values:
                    if w_loop == 6:
                        w_loop = 0

                    if w_loop == 0:
                        f.write(nl)
                        f.writelines('   WERT')

                    f.write('   ' + str(values))
                    w_loop += 1

                f.writelines(nl + 'END' + nl + nl)

        for line in dcm.rest:
            f.writelines(line + nl)

        f.close()
        return True
    return False


def compare_label(label_1, label_2):
    # interpolating values label_1 on label_2 axis
    # subtract values label_2 - label_1
    if label_1.typ.name == label_2.typ.name:
        new_label = label_2.copy()
        new_label.name += ' - delta'

        if label_1.typ.name == 'MAP':
            grid_x = np.array(label_1.typ.x_axis)
            grid_y = np.array(label_1.typ.y_axis)
            values_1 = np.array(label_1.typ.values).reshape((len(grid_y), len(grid_x)))
            new_x = np.array(label_2.typ.x_axis)
            new_y = np.array(label_2.typ.y_axis)
            values_2 = np.array(label_2.typ.values).reshape((len(label_2.typ.y_axis), len(label_2.typ.x_axis)))
            interp_fun = interp2d(grid_x, grid_y, values_1, kind='linear')
            interp_data = interp_fun(new_x, new_y)
            values_delta = (values_2 - interp_data).flatten()
            new_label.typ.values = values_delta.tolist()
            return new_label

        if label_1.typ.name == 'CUR':
            grid_x = np.array(label_1.typ.x_axis)
            grid_y = np.array([0, 1, 2])
            val = label_1.typ.values
            values_1 = np.array([val, val, val])
            new_x = np.array(label_2.typ.x_axis)
            new_y = np.array([1])
            values_2 = np.array(label_2.typ.values).reshape(1, len(label_2.typ.x_axis))
            interp_fun = interp2d(grid_x, grid_y, values_1, kind='linear')
            interp_data = interp_fun(new_x, new_y)
            values_delta = (values_2 - interp_data).flatten()
            new_label.typ.values = values_delta.tolist()
            return new_label

        if label_1.typ.name == 'C':
            new_label.typ.value = np.array(label_1.typ.value) - np.array(label_2.typ.value)
            return new_label

        if label_1.typ.name == 'CA':
            return new_label
        return False
    return False


def main():
    pass


if __name__ == '__main__':
    main()

__author__ = 'aktas&bakaj'
