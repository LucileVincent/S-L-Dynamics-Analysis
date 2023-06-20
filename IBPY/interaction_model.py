from IBPY.interaction_analysis import *
from IBPY.utils import AttributeGenerator, split_segments
import os


class Expression:
    def __init__(self, label, val, linked_files=None):
        """
        label (str) : expression name.
        val (tuple): (start, stop, value) format.
        linked_file (dict): link to data files like video or audio files.
                            In the format {key1:path_to_file1, key2:path_to_file2}
        We don't know if val is ordered or not"""
        self.label = label
        self.val = val
        self.linked_files = linked_files

    def replace_label(self, old, new):
        """Return list of (strt, stp, lab) with the old labels replaces by new."""
        if not isinstance(old, (list, tuple)):
            old = [old]
        if hasattr(old, "__iter__") and not isinstance(old, (list, tuple)):
            raise AttributeError("old must be a str, list or tuple")
        new_lst = [
            (strt, stp, new) if l in old else (strt, stp, l)
            for (strt, stp, l) in self.val
        ]
        return new_lst

    def get_duration(self):
        """considering that the list is unordered."""
        last = self.val[-1][2]
        for strt, stp, lab in self.val[-2::-1]:
            if stp <= last:
                break
            else:
                last = stp
        return last

    def label_count(self):
        """Return dictionnary of labels count."""
        dct = {}
        for _, _, lab in self.val:
            if lab not in cnt_dct:
                cnt_dct[lab] = 1
            else:
                cnt_dct[lab] += 1
        return cnt_dct

    def overlap_with(self, lst):
        dct = get_overlapping_segments(self, val, lst)
        return dct

    def split_segments(self, linked_files=None, dest_path=None, to=False):
        """split the corresponding files into the tier's values
        linked_files must be: {key1:path_to_file1, key2:path_to_file2}"""

        if linked_files is None:
            if self.linked_files is None:
                raise AttributeError("No linked files found.")
            else:
                linked_files = self.linked_files
        for mod,f in linked_files.items():
            if dest_path is None:
                dest_path_ = os.path.join(os.path.dirname(f), mod)
            else:
                dest_path_ =  os.path.join(dest_path, mod)
            if not os.path.exists(dest_path_):
                os.makedirs(dest_path_)
            split_segments(f, dest_path_, self.label, self.val, to)


class Subject(AttributeGenerator):
    """Represent an individual."""

    def __init__(self, subj_id, expr=None):
        self.id = subj_id
        self.add_expr(expr)

    def add_expr(self, expr):
        """Add expression to Subject instance."""
        if expr is not None:
            if isinstance(expr, Expression):
                expr = [expr]
            if not isinstance(expr, list):
                raise AttributeError(
                    "expr must be of type {} or list of {}".format(Expression.__name__)
                )
            for x in expr:
                super()._add(x.name, x.val)

    @property
    def expr_lst(self):
        """Return a list of expressions added."""
        return super()._list_attr

class Interaction:
    """Represent an interaction."""

    def __init__(self, subj_lst):
        if not isinstance(subj_lst, (list, tuple)):  # is list
            raise AttributeError("sub_lst must be a list or tuple")
        for subj in subj_lst:
            if not isinstance(subj, Subject):  # is Subject
                raise AttributeError("Input must be of type {}".format(Subject.__name))
            setattr(self, subj)  # add to attributes