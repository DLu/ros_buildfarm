import re
import collections

CANDIDATES = ['build', 'test', 'main']
VERSION_PATTERN = re.compile('([\d\-\.]+)\w+.*')


def map_check(M, needle, key):
    return M[key] == set(needle)


def some_value_check(M, needle):
    if type(needle) != set:
        needle = set(needle)
    for key in M.keys():
        if M[key] == needle:
            return True
    return False


def some_other_value_check(M, needle, exclude):
    if type(needle) != set:
        needle = set(needle)
    for key in M.keys():
        if key == exclude:
            continue
        if M[key] == needle:
            return True
    return False


def sub_filter(D, o_filter=None, d_filter=None, b_filter=None, c_filter=None):
    D2 = {}
    for os_name, os_d in D.iteritems():
        if o_filter == os_name:
            continue
        D2[os_name] = {}
        for os_distro, osd_d in os_d.iteritems():
            if d_filter == os_distro:
                continue
            D2[os_name][os_distro] = {}
            for binary_type, b_d in osd_d.iteritems():
                if b_filter == binary_type:
                    continue
                D2[os_name][os_distro][binary_type] = {}
                for candidate, v in b_d.iteritems():
                    if c_filter == candidate:
                        continue
                    D2[os_name][os_distro][binary_type][candidate] = v

    return {'build_status': D2}


def get_distro_status(D, expected, blacklist, candidates=CANDIDATES, skip_source=False):
    version_map = collections.defaultdict(list)
    os_map = collections.defaultdict(set)
    distro_map = collections.defaultdict(set)
    build_map = collections.defaultdict(set)
    level_map = collections.defaultdict(set)
    combo_map = collections.defaultdict(set)

    for os_name in expected:
        os_d = D.get(os_name, {})
        for os_distro in expected[os_name]:
            osd_d = os_d.get(os_distro, {})
            for binary_type in expected[os_name][os_distro]:
                if skip_source and binary_type == 'source':
                    continue
                b_d = osd_d.get(binary_type, {})
                for candidate in candidates:
                    version = None
                    if candidate in b_d:
                        version = VERSION_PATTERN.match(b_d[candidate]).group(1)
                    elif (os_name, os_distro, binary_type) in blacklist:
                        continue
                    os_map[version].add(os_name)
                    distro_map[version].add(os_distro)
                    build_map[version].add(binary_type)
                    level_map[version].add(candidate)
                    combo_map[version].add(os_distro + '/' + binary_type)
                    version_map[version].append((os_name, os_distro, binary_type, candidate))
    counts = {}
    for name, d in [('os', os_map), ('distro', distro_map), ('build_type', build_map), ('level', level_map)]:
        counts[name] = len(d)

    if sum(counts.values()) == 4:
        return 'released'

    if counts['level'] == 2:
        if map_check(level_map, ['main'], None):
            return 'waiting for new release'
        elif some_value_check(level_map, ['main']):
            return 'waiting for re-release'
    elif counts['level'] == 3:
        if map_check(level_map, ['main'], None) and some_other_value_check(level_map, ['main'], None):
            return 'waiting for new/re-release'

    if counts['build_type'] == 2:
        a, b = sorted(build_map.keys())
        if map_check(build_map, ['source'], a):
            return 'source builds, binary doesn\'t'
        elif b is not None and map_check(build_map, ['source'], b):
            return 'source builds, binary doesn\'t'

    if counts['distro'] == 2:
        a, b = distro_map.values()
        if len(a.intersection(b)) == 0 and None in distro_map:
            value = distro_map[None]
            return 'does not build on ' + ', '.join(list(value))

    if counts['build_type'] == 2:
        a, b = build_map.values()
        if len(a.intersection(b)) == 0 and None in build_map:
            value = build_map[None]
            return 'does not build on ' + ', '.join(list(value))

    if len(combo_map) == 2:
        a, b = combo_map.values()
        if len(a.intersection(b)) == 0 and None in combo_map:
            value = combo_map[None]
            return 'does not build on ' + ', '.join(list(value))

    if None in version_map:
        values = version_map[None]
        DX = set([(os_distro, binary_type) for os_name, os_distro, binary_type, candidate in values])
        if len(DX) == 1:
            a, b = list(DX)[0]
            return "doesn't build on %s/%s" % (a, b)

    if candidates == CANDIDATES:
        sub_candidates = CANDIDATES[:-1]  # skip main
        status = get_distro_status(D, expected, blacklist, sub_candidates)
        if status and status != 'released':
            return status

        status = get_distro_status(D, expected, blacklist, sub_candidates, True)
        if status and status != 'released':
            return 'binary: ' + status

    if len(combo_map) == 2 and None in combo_map:
        value = combo_map[None]
        return 'does not build on ' + ', '.join(list(value))

    print dict(os_map)
    print dict(distro_map)
    print dict(build_map)
    print dict(level_map)
    print dict(combo_map)
    print counts
    for k, v in version_map.items():
        for m in v:
            print k, m
    print
    # exit(0)

    """
    if counts['level'] == 3:
        vs = sorted(level_map.keys(), cmp=version_sort)
        if map_check(level_map, ['public'], vs[0]) and \
           map_check(level_map, ['public'], vs[1]) and \
           map_check(level_map, ['shadow', 'build'], vs[2]):
            return 'waiting for first full release'

    if counts['distro'] == 2:
        a, b = distro_map.values()
        if len(a) == 1:
            return 'trouble building ' + list(a)[0]

    if counts['level'] >= 3:
        return 'multiple versions'

    if whiny:
        print '\n'
        print counts['build_type']
        for k, v in the_maps.iteritems():
            print k
            for a, b in v.iteritems():
                print ' ', a, b
        for v in self.version_map:
            print v, len(self.version_map[v])
            if v == 'None':
                print self.version_map[v]
        return 'unknown'
    return self.status
    """


def get_aggregate_status(D, expected, pkg_name=None, blacklist={}):
    per_distro = {}
    for distro in sorted(D):
        if distro == 'maintainers':
            continue
        status = get_distro_status(D[distro]['build_status'], expected[distro], blacklist.get(pkg_name, {}).get(distro, set()))
        per_distro[distro] = status

    return per_distro
