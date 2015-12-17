import subprocess, os, sys

_FIELDSEP = " | "
_VERBOSE = False

###############################################################################
def set_verbosity(is_verbose):
###############################################################################
    global _VERBOSE
    _VERBOSE = is_verbose

###############################################################################
def warning(msg):
###############################################################################
    """
    Print a warning to stderr
    """
    print >> sys.stderr, "WARNING:", msg

###############################################################################
def expect(condition, error_msg):
###############################################################################
    """
    Similar to assert except doesn't generate an ugly stacktrace. Useful for
    checking user error, not programming error.
    """
    if (not condition):
        raise SystemExit("FAIL: %s" % error_msg)

###############################################################################
def verbose_print(msg, override=None):
###############################################################################
    if ( (_VERBOSE and not override is False) or override):
        print msg

###############################################################################
def run_cmd(cmd, ok_to_fail=False, input_str=None, from_dir=None, verbose=None,
            arg_stdout=subprocess.PIPE, arg_stderr=subprocess.PIPE):
###############################################################################
    """
    Wrapper around subprocess to make it much more convenient to run shell commands
    """
    verbose_print("RUN: %s" % cmd, verbose)

    if (input_str is not None):
        stdin = subprocess.PIPE
    else:
        stdin = None

    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdout=arg_stdout,
                            stderr=arg_stderr,
                            stdin=stdin,
                            cwd=from_dir)
    output, errput = proc.communicate(input_str)
    output = output.strip() if output is not None else output
    errput = errput.strip() if errput is not None else errput
    stat = proc.wait()

    verbose_print("  stat: %d\n" % stat, verbose)
    verbose_print("  output: %s\n" % output, verbose)
    verbose_print("  errput: %s\n" % errput, verbose)

    if (ok_to_fail):
        return stat, output, errput
    else:
        if (arg_stderr is not None):
            errput = errput if errput is not None else open(arg_stderr.name, "r").read()
            expect(stat == 0, "Command: '%s' failed with error '%s'" % (cmd, errput))
        else:
            expect(stat == 0, "Command: '%s' failed. See terminal output" % cmd)
        return output

###############################################################################
def read_db_file(dbfile):
###############################################################################
    with open(dbfile, "r") as fd:
        lines = fd.readlines()

    events = []
    for line in lines:
        if (line.strip()):
            events.append(line.split(_FIELDSEP))
            expect(len(events[-1]) == 3,
                   "Line '%s' in wrong format" % line)
            events[-1][2] = int(events[-1][2])
            events[-1] = tuple(events[-1])

    return events

###############################################################################
def write_db_file(dbfile, events):
###############################################################################
    text = ""
    for event in events:
        text += "%s\n" % (_FIELDSEP.join([str(item) for item in event]))

    with open(dbfile, "w") as fd:
        fd.write(text)

###############################################################################
def update_db_file(dbfile, events):
###############################################################################
    old_events = []
    if (os.path.exists(dbfile)):
        old_events = read_db_file(dbfile)

    if (events[0] in old_events):
        merge_idx = old_events.index(events[0])
        num_events = len(events)
        num_old_events = len(old_events) - merge_idx
        num_new_events = num_events - num_old_events
        if (num_new_events > 0):
            print
            for new_event in events[-num_new_events:]:
                print "Found new event: %s" % new_event
                old_events.append(new_event)

    else:
        warning("Gap in coverage!")
        old_events.extend(events)


    write_db_file(dbfile, old_events)

