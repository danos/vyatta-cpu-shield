#
# Copyright (c) 2017-2018, AT&T Intellectual Property.  All rights reserved.
#
# SPDX-License-Identifier: LGPL-2.1-only
#
""" This module provides a class that can be used to manipulate cpusets """

class Cpuset(object):
    """ Create and manipulate a set of cpus. """

    def __init__(self, cpus, mask=False):
        """ Create a cpuset from a range or mask of cpus. """
        self.cpus = cpus.strip()

        if mask:
            self.cpus = Cpuset._mask_to_range(cpus.strip())

    @staticmethod
    def _mask_to_range(mask):
        """ Convert a mask of cpus into a range of cpus. """
        cpus = mask[::-1] # reverse the string
        all_cpus = ""

        start = -1
        last = 0
        count = 0
        sep = ''
        for char in cpus:
            for i in range(0, 4):
                char_mask = 1 << i
                if char_mask & int(char, 16):
                    bit = i + count
                    # bit is set.
                    if start >= 0:
                        if bit == last + 1:
                            # continuation of range
                            last = bit
                    else:
                        #start of new range
                        start = bit
                        last = bit
                        all_cpus += sep + str(bit)
                        sep = ','
                else:
                    if start >= 0:
                        if start != last:
                            #end of range
                            all_cpus += "-" + str(bit)
                    start = -1
            count = count + 4

        #Terminate open range
        if start >= 0:
            if start != last:
                all_cpus += "-" + str(last)

        return all_cpus

    @staticmethod
    def _list_to_range(_list):
        """ Convert a list of cpus into a range of cpus. """
        mask = 0
        for num in _list.split(','):
            mask = mask +  (1 << int(num))
        mask = format(mask, 'x')
        return Cpuset._mask_to_range(mask)

    def _range_to_list(self):
        """ Return a string that show the cpus in a cpuset as a list. """

        if self.cpus == '':
            return ''

        all_cpus = ""
        sep = ""
        _list = self.cpus.split(',')
        for val in _list:
            if '-' in val:
                nums = val.split('-')
                for i in range(int(nums[0]), int(nums[1]) + 1):
                    all_cpus += sep
                    all_cpus += str(i)
                    sep = ","
            else:
                all_cpus += sep
                all_cpus += str(val)
                sep = ","

        return all_cpus

    def _range_to_mask(self):
        """ Return a string that show the cpus in a cpuset as a mask. """
        if self.cpus == '':
            return ''

        _list = self._range_to_list()
        mask = 0
        for val in _list.split(','):
            mask = mask +  (1 << int(val))

        m = format(mask, 'x')
        start=len(m)%8
        mslw = m[:start] + ',' if start != 0 else ""
        return mslw + ','.join([m[i:i+8] for i in range(start,len(m),8)])

    def range(self):
        """ Return a string that shows the cpus in a cpuset as a range. """
        return self.cpus

    def list(self):
        """ Return a string that shows the cpus in a cpuset as a list. """
        return self._range_to_list()

    def mask(self):
        """ Return a string that shows the cpus in a cpuset as a mask. """
        return self._range_to_mask()

    def add_cpuset(self, cpuset):
        """ Add the cpus in the cpuset to self. """
        cpuset_a = self.list().split(',')
        cpuset_b = cpuset.list().split(',')

        cpus = ""
        sep = ""
        for cpu in cpuset_a:
            if cpu.isdigit():
                cpus += sep
                cpus += str(cpu)
                sep = ","
        for cpu in cpuset_b:
            if cpu not in cpuset_a:
                if cpu.isdigit():
                    cpus += sep
                    cpus += str(cpu)
                    sep = ","
        self.cpus = Cpuset._list_to_range(cpus)

    def remove_cpuset(self, cpuset):
        """ Remove the cpus in the cpuset from self. May leave it empty. """
        cpus = ""
        sep = ""
        for cpu in self.list().split(','):
            if cpu not in cpuset.list().split(','):
                if cpu.isdigit():
                    cpus += sep
                    cpus += str(cpu)
                    sep = ","
        if cpus == "":
            self.cpus = ""
        else:
            self.cpus = Cpuset._list_to_range(cpus)
