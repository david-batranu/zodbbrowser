from pprint import pformat
from pprint import pprint
from zope.publisher.browser import BrowserView


def zodb_objects_by_size(context):
    """
        Recurse over the ZODB tree starting from self.aq_parent. For
        each object, use zodbbrowser's implementation to get the raw
        object state. Put each length into a Counter object and
        return a list of the biggest objects, specified by path and
        size.
    """
    from zodbbrowser.history import ZodbObjectHistory
    from collections import Counter

    def recurse(obj, results):
        # Retrieve state pickle from ZODB, get length
        history = ZodbObjectHistory(obj)
        try:
            pstate = history.loadStatePickle()
        except TypeError:
            return
        length = len(pstate)

        # Add length to Counter instance
        path = '/'.join(obj.getPhysicalPath())
        results[path] = length

        sub_objects = obj.objectValues()

        have_connection = tuple(
            child for child in sub_objects
            if getattr(child, '_p_jar', None) is not None
        )

        and_are_not_parent = tuple(
            child for child in have_connection
            if child.objectValues() != sub_objects
        )

        # Recursion
        for child in and_are_not_parent:
            recurse(child, results)

    results = Counter()
    recurse(context, results)
    return results


class RecurseSizeView(BrowserView):
    def __call__(self):
        result = zodb_objects_by_size(self.context)
        most_common = result.most_common()
        pprint(most_common)
        print(sum(result.values()) / 1024, 'KB')
        return pformat(most_common)