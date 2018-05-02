import re, string

class Version:
    """Abstract base class for version numbering classes.  Just provides
    constructor (__init__) and reproducer (__repr__), because those
    seem to be the same for all version numbering classes.
    """

    def __init__ (self, vstring=None):
        if vstring:
            self.parse(vstring)

    def __repr__ (self):
        return "%s ('%s')" % (self.__class__.__name__, str(self))


# Interface for version-number classes -- must be implemented
# by the following classes (the concrete ones -- Version should
# be treated as an abstract class).
#    __init__ (string) - create and take same action as 'parse'
#                        (string parameter is optional)
#    parse (string)    - convert a string representation to whatever
#                        internal representation is appropriate for
#                        this style of version numbering
#    __str__ (self)    - convert back to a string; should be very similar
#                        (if not identical to) the string supplied to parse
#    __repr__ (self)   - generate Python code to recreate
#                        the instance
#    __cmp__ (self, other) - compare two version numbers ('other' may
#                        be an unparsed version string, or another
#                        instance of your version class)


class StrictVersion (Version):

    """Version numbering for anal retentives and software idealists.
    Implements the standard interface for version number classes as
    described above.  A version number consists of two or three
    dot-separated numeric components, with an optional "pre-release" tag
    on the end.  The pre-release tag consists of the letter 'a' or 'b'
    followed by a number.  If the numeric components of two version
    numbers are equal, then one with a pre-release tag will always
    be deemed earlier (lesser) than one without.

    The following are valid version numbers (shown in the order that
    would be obtained by sorting according to the supplied cmp function):

        0.4       0.4.0  (these two are equivalent)
        0.4.1
        0.5a1
        0.5b3
        0.5
        0.9.6
        1.0
        1.0.4a3
        1.0.4b1
        1.0.4

    The following are examples of invalid version numbers:

        1
        2.7.2.2
        1.3.a4
        1.3pl1
        1.3c4

    The rationale for this version numbering system will be explained
    in the distutils documentation.
    """

    version_re = re.compile(r'^(\d+) \. (\d+) (\. (\d+))? ([ab](\d+))?$',
                            re.VERBOSE)


    def parse (self, vstring):
        match = self.version_re.match(vstring)
        if not match:
            raise ValueError, "invalid version number '%s'" % vstring

        (major, minor, patch, prerelease, prerelease_num) = \
            match.group(1, 2, 4, 5, 6)

        if patch:
            self.version = tuple(map(string.atoi, [major, minor, patch]))
        else:
            self.version = tuple(map(string.atoi, [major, minor]) + [0])

        if prerelease:
            self.prerelease = (prerelease[0], string.atoi(prerelease_num))
        else:
            self.prerelease = None


    def __str__ (self):

        if self.version[2] == 0:
            vstring = string.join(map(str, self.version[0:2]), '.')
        else:
            vstring = string.join(map(str, self.version), '.')

        if self.prerelease:
            vstring = vstring + self.prerelease[0] + str(self.prerelease[1])

        return vstring


    def __cmp__ (self, other):
        if isinstance(other, str):
            other = StrictVersion(other)

        compare = cmp(self.version, other.version)
        if (compare == 0):              # have to compare prerelease

            # case 1: neither has prerelease; they're equal
            # case 2: self has prerelease, other doesn't; other is greater
            # case 3: self doesn't have prerelease, other does: self is greater
            # case 4: both have prerelease: must compare them!

            if (not self.prerelease and not other.prerelease):
                return 0
            elif (self.prerelease and not other.prerelease):
                return -1
            elif (not self.prerelease and other.prerelease):
                return 1
            elif (self.prerelease and other.prerelease):
                return cmp(self.prerelease, other.prerelease)

        else:                           # numeric versions don't match --
            return compare              # prerelease stuff doesn't matter


# end class StrictVersion


# The rules according to Greg Stein:
# 1) a version number has 1 or more numbers separated by a period or by
#    sequences of letters. If only periods, then these are compared
#    left-to-right to determine an ordering.
# 2) sequences of letters are part of the tuple for comparison and are
#    compared lexicographically
# 3) recognize the numeric components may have leading zeroes
#
# The LooseVersion class below implements these rules: a version number
# string is split up into a tuple of integer and string components, and
# comparison is a simple tuple comparison.  This means that version
# numbers behave in a predictable and obvious way, but a way that might
# not necessarily be how people *want* version numbers to behave.  There
# wouldn't be a problem if people could stick to purely numeric version
# numbers: just split on period and compare the numbers as tuples.
# However, people insist on putting letters into their version numbers;
# the most common purpose seems to be:
#   - indicating a "pre-release" version
#     ('alpha', 'beta', 'a', 'b', 'pre', 'p')
#   - indicating a post-release patch ('p', 'pl', 'patch')
# but of course this can't cover all version number schemes, and there's
# no way to know what a programmer means without asking him.
#
# The problem is what to do with letters (and other non-numeric
# characters) in a version number.  The current implementation does the
# obvious and predictable thing: keep them as strings and compare
# lexically within a tuple comparison.  This has the desired effect if
# an appended letter sequence implies something "post-release":
# eg. "0.99" < "0.99pl14" < "1.0", and "5.001" < "5.001m" < "5.002".
#
# However, if letters in a version number imply a pre-release version,
# the "obvious" thing isn't correct.  Eg. you would expect that
# "1.5.1" < "1.5.2a2" < "1.5.2", but under the tuple/lexical comparison
# implemented here, this just isn't so.
#
# Two possible solutions come to mind.  The first is to tie the
# comparison algorithm to a particular set of semantic rules, as has
# been done in the StrictVersion class above.  This works great as long
# as everyone can go along with bondage and discipline.  Hopefully a
# (large) subset of Python module programmers will agree that the
# particular flavour of bondage and discipline provided by StrictVersion
# provides enough benefit to be worth using, and will submit their
# version numbering scheme to its domination.  The free-thinking
# anarchists in the lot will never give in, though, and something needs
# to be done to accommodate them.
#
# Perhaps a "moderately strict" version class could be implemented that
# lets almost anything slide (syntactically), and makes some heuristic
# assumptions about non-digits in version number strings.  This could
# sink into special-case-hell, though; if I was as talented and
# idiosyncratic as Larry Wall, I'd go ahead and implement a class that
# somehow knows that "1.2.1" < "1.2.2a2" < "1.2.2" < "1.2.2pl3", and is
# just as happy dealing with things like "2g6" and "1.13++".  I don't
# think I'm smart enough to do it right though.
#
# In any case, I've coded the test suite for this module (see
# ../test/test_version.py) specifically to fail on things like comparing
# "1.2a2" and "1.2".  That's not because the *code* is doing anything
# wrong, it's because the simple, obvious design doesn't match my
# complicated, hairy expectations for real-world version numbers.  It
# would be a snap to fix the test suite to say, "Yep, LooseVersion does
# the Right Thing" (ie. the code matches the conception).  But I'd rather
# have a conception that matches common notions about version numbers.

class LooseVersion (Version):

    """Version numbering for anarchists and software realists.
    Implements the standard interface for version number classes as
    described above.  A version number consists of a series of numbers,
    separated by either periods or strings of letters.  When comparing
    version numbers, the numeric components will be compared
    numerically, and the alphabetic components lexically.  The following
    are all valid version numbers, in no particular order:

        1.5.1
        1.5.2b2
        161
        3.10a
        8.02
        3.4j
        1996.07.12
        3.2.pl0
        3.1.1.6
        2g6
        11g
        0.960923
        2.2beta29
        1.13++
        5.5.kw
        2.0b1pl0

    In fact, there is no such thing as an invalid version number under
    this scheme; the rules for comparison are simple and predictable,
    but may not always give the results you want (for some definition
    of "want").
    """

    component_re = re.compile(r'(\d+ | [a-z]+ | \.)', re.VERBOSE)

    def __init__ (self, vstring=None):
        if vstring:
            self.parse(vstring)


    def parse (self, vstring):
        # I've given up on thinking I can reconstruct the version string
        # from the parsed tuple -- so I just store the string here for
        # use by __str__
        self.vstring = vstring
        components = filter(lambda x: x and x != '.',
                            self.component_re.split(vstring))
        for i in range(len(components)):
            try:
                components[i] = int(components[i])
            except ValueError:
                pass

        self.version = components


    def __str__ (self):
        return self.vstring


    def __repr__ (self):
        return "LooseVersion ('%s')" % str(self)


    def __cmp__ (self, other):
        if isinstance(other, str):
            other = LooseVersion(other)

        return cmp(self.version, other.version)

def split_version(name):
    try:
        match = re_split_version.search(name)
        addon_id, version = match.groups()
        return addon_id, version
    except:
        return False, False
# end class LooseVersion

re_plugin = re.compile("^plugin\.", re.IGNORECASE)
re_service = re.compile("^service\.", re.IGNORECASE)
re_script = re.compile("^script\.", re.IGNORECASE)
re_repository = re.compile("^repository\.", re.IGNORECASE)
re_program = re.compile("^(program\.)|(plugin\.program)", re.IGNORECASE)
re_skin = re.compile("^skin\.", re.IGNORECASE)
re_version = re.compile("-([^zip]+)\.zip$")
re_split_version = re.compile("^(.+?)-([^zip]+)\.zip$")

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    forward = dict((key, value) for key, value in enums.iteritems())
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['f_map'] = forward
    enums['r_map'] = reverse
    return type('Enum', (), enums)

def get_version_by_name(name):
    version = re_version.search(name)
    if version:
        return version.group(1)
    else:
        return '0.0.0'
SORT_ORDER = enum(REPO=0, PLUGIN=1, PROGRAM=2, SKIN=3, SERVICE=4, SCRIPT=5, OTHER=100)

def sort_results(results):
    def sort_results(name):
        index = SORT_ORDER.OTHER
        version = get_version_by_name(name)
        version_index = LooseVersion(version)
        if re_program.search(name): index = SORT_ORDER.PROGRAM
        elif re_plugin.search(name): index = SORT_ORDER.PLUGIN
        elif re_repository.search(name): index = SORT_ORDER.REPO
        elif re_service.search(name): index = SORT_ORDER.SERVICE
        elif re_script.search(name): index = SORT_ORDER.SCRIPT
        return index, name.lower(), version_index

    return sorted(results, key=lambda x:sort_results(x['name']), reverse=False)
#return sorted(temp, key=lambda x: x['name'])

def limit_versions(results):
    final = []
    temp = []
    sorted_results = sort_results(results['items'])
    print '@@@@@@@@@@@@@@@@@@'
    #print sorted_results
    for a in sorted_results:
        addon_id, version = split_version(a['name'])
        print 'addonid %s version %s ' % (addon_id, version)
        if addon_id in temp: continue
        final.append(a)
        print 'FINAL'
        print a
        temp.append(addon_id)
    results['items'] = final
    return results

params = {'items': [{'name':'repository.aftershock-2017.07.10.zip'}, {'name':'repository.aftershock-2018.04.06.zip'}, {'name':'plugin.video.swadesi-2017.07.10'}, {'name':'plugin.video.swadesi-2018.04.06'}]}


result=limit_versions(params)
print 'RESULT'
print result
