'''Utilities.py - Tools for writing reproducible scripts
=========================================================

The :mod:`Utilities` modules contains utility functions for argument
parsing, logging and record keeping within scripts.

This module is imported by most UMI-tools tools. It provides convenient
and consistent methods for

   * `Record keeping`_
   * `Argument parsing`_
   * `Input/Output redirection`_
   * `Logging`_
   * `Running external commands`_
   * `Benchmarking`_

The basic usage of this module within a script is::

    """script_name.py - my script

    Mode Documentation
    """
    import sys
    import optparse
    import Utilities as U

    def main(argv=None):
        """script main.

        parses command line options in sys.argv, unless *argv* is given.
        """

        if not argv: argv = sys.argv

        # setup command line parser
        parser = U.OptionParser(version="%prog version: $Id$",
                                usage=globals()["__doc__"] )

        parser.add_option("-t", "--test", dest="test", type="string",
                          help="supply help")

        # add common options (-h/--help, ...) and parse
        # command line
        (options, args) = U.Start(parser)

        # do something
        # ...
        U.info("an information message")
        U.warn("a warning message)

        ## write footer and output benchmark information.
        U.Stop()

    if __name__ == "__main__":
        sys.exit(main(sys.argv))

Record keeping
--------------

The central functions in this module are the :py:func:`Start` and
:py:func:`Stop` methods which are called before or after any work is
done within a script.

The :py:func:`Start` is called with an U.OptionParser object.
:py:func:`Start` will add additional command line arguments, such as
``--help`` for command line help or ``--verbose`` to control the
:term:`loglevel`.  It can also add optional arguments for scripts
needing database access, writing to multiple output files, etc.

:py:func:`Start` will write record keeping information to a
logfile. Typically, logging information is output on stdout, prefixed
by a `#`, but it can be re-directed to a separate file. Below is a
typical output::

    # output generated by /ifs/devel/andreas/cgat/beds2beds.py --force-output --exclusive-overlap --method=unmerged-combinations --output-filename-pattern=030m.intersection.tsv.dir/030m.intersection.tsv-%s.bed.gz --log=030m.intersection.tsv.log Irf5-030m-R1.bed.gz Rela-030m-R1.bed.gz
    # job started at Thu Mar 29 13:06:33 2012 on cgat150.anat.ox.ac.uk -- e1c16e80-03a1-4023-9417-f3e44e33bdcd
    # pid: 16649, system: Linux 2.6.32-220.7.1.el6.x86_64 #1 SMP Fri Feb 10 15:22:22 EST 2012 x86_64
    # exclusive                               : True
    # filename_update                         : None
    # ignore_strand                           : False
    # loglevel                                : 1
    # method                                  : unmerged-combinations
    # output_filename_pattern                 : 030m.intersection.tsv.dir/030m.intersection.tsv-%s.bed.gz
    # output_force                            : True
    # pattern_id                              : (.*).bed.gz
    # stderr                                  : <open file \'<stderr>\', mode \'w\' at 0x2ba70e0c2270>
    # stdin                                   : <open file \'<stdin>\', mode \'r\' at 0x2ba70e0c2150>
    # stdlog                                  : <open file \'030m.intersection.tsv.log\', mode \'a\' at 0x1f1a810>
    # stdout                                  : <open file \'<stdout>\', mode \'w\' at 0x2ba70e0c21e0>
    # timeit_file                             : None
    # timeit_header                           : None
    # timeit_name                             : all
    # tracks                                  : None

The header contains information about:

    * the script name (``beds2beds.py``)

    * the command line options (``--force-output --exclusive-overlap
      --method=unmerged-combinations
      --output-filename-pattern=030m.intersection.tsv.dir/030m.intersection.tsv-%s.bed.gz
      --log=030m.intersection.tsv.log Irf5-030m-R1.bed.gz
      Rela-030m-R1.bed.gz``)

    * the time when the job was started (``Thu Mar 29 13:06:33 2012``)
    * the location it was executed (``cgat150.anat.ox.ac.uk``)
    * a unique job id (``e1c16e80-03a1-4023-9417-f3e44e33bdcd``)
    * the pid of the job (``16649``)

    * the system specification (``Linux 2.6.32-220.7.1.el6.x86_64 #1
      SMP Fri Feb 10 15:22:22 EST 2012 x86_64``)

It is followed by a list of all options that have been set in the script.

Once completed, a script will call the :py:func:`Stop` function to
signify the end of the experiment.

:py:func:`Stop` will output to the log file that the script has
concluded successfully. Below is typical output::

    # job finished in 11 seconds at Thu Mar 29 13:06:44 2012 -- 11.36 0.45 0.00 0.01 -- e1c16e80-03a1-4023-9417-f3e44e33bdcd

The footer contains information about:

   * the job has finished (``job finished``)
   * the time it took to execute (``11 seconds``)
   * when it completed (``Thu Mar 29 13:06:44 2012``)
   * some benchmarking information (``11.36  0.45  0.00  0.01``)
     which is ``user time``, ``system time``,
     ``child user time``, ``child system time``.
   * the unique job id (``e1c16e80-03a1-4023-9417-f3e44e33bdcd``)

The unique job id can be used to easily retrieve matching information
from a concatenation of log files.

Argument parsing
----------------

The module provides :class:`OptionParser` to facilitate option
parsing.  :class:`OptionParser` is derived from the
:py:class:`optparse.OptionParser` class, but has improvements to
provide better formatted output on the command line. It also allows to
provide a comma-separated list to options that accept multiple
arguments. Thus, ``--method=sort --method=crop`` and
``--method=sort,crop`` are equivalent.

Input/Output redirection
------------------------

:func:`Start` adds the options ``--stdin``, ``--stderr` and
``--stdout`` which allow using files as input/output streams.

To make this work, scripts should not read from sys.stdin or write to
sys.stdout directly, but instead use ``options.stdin`` and
``options.stdout``. For example to simply read all lines from stdin
and write to stdout, use::

   (options, args) = U.Start(parser)

   input_data = options.stdin.readlines()
   options.stdout.write("".join(input_data))

The script can then be used in many different contexts::

   cat in.data | python script.py > out.data
   python script.py --stdin=in.data > out.data
   python script.py --stdin=in.data --stdout=out.data

The method handles gzip compressed files transparently. The following
are equivalent::

   zcat in.data.gz | python script.py | gzip > out.data.gz
   python script.py --stdin=in.data.gz --stdout=out.data.gz

For scripts producing multiple output files, use the argument
``add_output_options=True`` to :func:`Start`. This provides the option
``--output-filename-pattern`` on the command line. The user can then
supply a pattern for output files. Any ``%s`` appearing in the pattern
will be substituted by a ``section``. Inside the script, When opening
an output file, use the method :func:`openOutputFile` to provide a
file object::

   output_histogram = U.openOutputFile(section="histogram")
   output_stats = U.openOutputFile(section="stats")

If the user calls the script with::

   python script.py --output-filename-pattern=sample1_%s.tsv.gz

the script will create the files ``sample1_histogram.tsv.gz`` and
``sample1_stats.tsv.gz``.

This method will also add the option ``--force-output`` to permit
overwriting existing files.

Logging
-------

:py:mod:`Utilities` provides the well known logging methods from
the :py:mod:`logging` module such as :py:func:`info`,
:py:func:`warn`, etc. These are provided so that no additional import
of the :py:mod:`logging` module is required, but either functions
can be used.

Running external commands
-------------------------

The :func:`run` method is a shortcut :py:func:`subprocess.call` and
similar methods with some additional sanity checking.

Benchmarking
------------

The :func:`Start` method records basic benchmarking information when a
script starts and :func:`Stop` outputs it as part of its final log
message::

    # job finished in 11 seconds at Thu Mar 29 13:06:44 2012 -- 11.36 0.45 0.00 0.01 -- e1c16e80-03a1-4023-9417-f3e44e33bdcd

See `Record keeping`_ for an explanations of the fields.

To facilitate collecting benchmark information from running multiple
scripts, these data can be tagged and saved in a separate file. See the
command line options ``--timeit``, ``--timeit-name``, ``--timeit-header``
in :func:`Start`.

The module contains some decorator functions for benchmarking
(:func:`benchmark`) and caching function (:func:`cachedfunction`) or
class method (:func:`cachedmethod`) calls.

Complete reference
------------------

'''

############################################################################
# The code for Utilities.py has been taken directly from CGAT.Experiment.py
# https://github.com/CGATOxford/cgat/blob/master/CGAT/Experiment.py
############################################################################


import re
import sys
import time
import inspect
import copy
import os
import logging
import collections
import gzip
import optparse
import textwrap
import random
import uuid


class DefaultOptions:
    stdlog = sys.stdout
    stdout = sys.stdout
    stderr = sys.stderr
    stdin = sys.stdin
    loglevel = 2
    timeit_file = None

global_starting_time = time.time()
global_options = DefaultOptions()
global_args = None
global_id = uuid.uuid4()
global_benchmark = collections.defaultdict(int)

##########################################################################
# The code for BetterFormatter has been taken from
# http://code.google.com/p/yjl/source/browse/Python/snippet/BetterFormatter.py
__copyright__ = """
Copyright (c) 2001-2006 Gregory P. Ward.  All rights reserved.
Copyright (c) 2002-2006 Python Software Foundation.  All rights reserved.
Copyright (c) 2011 Yu-Jie Lin.  All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

  * Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.

  * Neither the name of the author nor the names of its
    contributors may be used to endorse or promote products derived from
    this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


class BetterFormatter(optparse.IndentedHelpFormatter):
    """A formatter for :class:`OptionParser` outputting indented
    help text.
    """

    def __init__(self, *args, **kwargs):

        optparse.IndentedHelpFormatter.__init__(self, *args, **kwargs)
        self.wrapper = textwrap.TextWrapper(width=self.width)

    def _formatter(self, text):

        return '\n'.join(['\n'.join(p) for p in
                          map(self.wrapper.wrap,
                              self.parser.expand_prog_name(text).split('\n'))])

    def format_description(self, description):

        if description:
            return self._formatter(description) + '\n'
        else:
            return ''

    def format_epilog(self, epilog):

        if epilog:
            return '\n' + self._formatter(epilog) + '\n'
        else:
            return ''

    def format_usage(self, usage):

        return self._formatter(optparse._("Usage: %s\n") % usage)

    def format_option(self, option):
        # Ripped and modified from Python 2.6's optparse's HelpFormatter
        result = []
        opts = self.option_strings[option]
        opt_width = self.help_position - self.current_indent - 2
        if len(opts) > opt_width:
            opts = "%*s%s\n" % (self.current_indent, "", opts)
            indent_first = self.help_position
        else:                       # start help on same line as opts
            opts = "%*s%-*s  " % (self.current_indent, "", opt_width, opts)
            indent_first = 0
        result.append(opts)
        if option.help:
            help_text = self.expand_default(option)
            # Added expand program name
            help_text = self.parser.expand_prog_name(help_text)
            # Modified the generation of help_line
            help_lines = []
            wrapper = textwrap.TextWrapper(width=self.help_width)
            for p in map(wrapper.wrap, help_text.split('\n')):
                if p:
                    help_lines.extend(p)
                else:
                    help_lines.append('')
            # End of modification
            result.append("%*s%s\n" % (indent_first, "", help_lines[0]))
            result.extend(["%*s%s\n" % (self.help_position, "", line)
                           for line in help_lines[1:]])
        elif opts[-1] != "\n":
            result.append("\n")
        return "".join(result)


# End of BetterFormatter()
#################################################################
#################################################################
#################################################################
class AppendCommaOption(optparse.Option):

    '''Option with additional parsing capabilities.

    * "," in arguments to options that have the action 'append'
      are treated as a list of options. This is what galaxy does,
      but generally convenient.

    * Option values of "None" and "" are treated as default values.
    '''
#    def check_value( self, opt, value ):
# do not check type for ',' separated lists
#        if "," in value:
#            return value
#        else:
#            return optparse.Option.check_value( self, opt, value )
#
#    def take_action(self, action, dest, opt, value, values, parser):
#        if action == "append" and "," in value:
#            lvalue = value.split(",")
#            values.ensure_value(dest, []).extend(lvalue)
#        else:
#            optparse.Option.take_action(
#                self, action, dest, opt, value, values, parser)
#

    def convert_value(self, opt, value):
        if value is not None:
            if self.nargs == 1:
                if self.action == "append":
                    if "," in value:
                        return [self.check_value(opt, v) for v in
                                value.split(",") if v != ""]
                    else:
                        if value != "":
                            return self.check_value(opt, value)
                        else:
                            return value
                else:
                    return self.check_value(opt, value)
            else:
                return tuple([self.check_value(opt, v) for v in value])

    # why is it necessary to pass action and dest to this function when
    # they could be accessed as self.action and self.dest?
    def take_action(self, action, dest, opt, value, values, parser):

        if action == "append" and type(value) == list:
            values.ensure_value(dest, []).extend(value)
        else:
            optparse.Option.take_action(
                self, action, dest, opt, value, values, parser)


class OptionParser(optparse.OptionParser):

    '''UMI-tools derivative of OptionParser.
    '''

    def __init__(self, *args, **kwargs):
        # if "--short" is a command line option
        # remove usage from kwargs
        if "--no-usage" in sys.argv:
            kwargs["usage"] = None

        optparse.OptionParser.__init__(self, *args,
                                       option_class=AppendCommaOption,
                                       formatter=BetterFormatter(),
                                       **kwargs)

        # set new option parser
        # parser.formatter = BetterFormatter()
        # parser.formatter.set_parser(parser)
        if "--no-usage" in sys.argv:
            self.add_option("--no-usage", dest="help_no_usage",
                            action="store_true",
                            help="output help without usage information")


class OptionGroup(optparse.OptionGroup):
    pass


def callbackShortHelp(option, opt, value, parser):
    '''output short help (only command line options).'''
    # clear usage and description
    parser.set_description(None)
    parser.set_usage(None)
    # output help
    parser.print_help()
    # exit
    parser.exit()


def openFile(filename, mode="r", create_dir=False):
    '''open file in *filename* with mode *mode*.

    If *create* is set, the directory containing filename
    will be created if it does not exist.

    gzip - compressed files are recognized by the
    suffix ``.gz`` and opened transparently.

    Note that there are differences in the file
    like objects returned, for example in the
    ability to seek.

    returns a file or file-like object.
    '''

    _, ext = os.path.splitext(filename)

    if create_dir:
        dirname = os.path.dirname(filename)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)

    if ext.lower() in (".gz", ".z"):
        return gzip.open(filename, mode)
    else:
        return open(filename, mode)


def getHeader():
    """return a header string with command line options and timestamp

    """
    system, host, release, version, machine = os.uname()

    return "# output generated by %s\n# job started at %s on %s -- %s\n# pid: %i, system: %s %s %s %s" %\
           (" ".join(sys.argv),
            time.asctime(time.localtime(time.time())),
            host,
            global_id,
            os.getpid(),
            system, release, version, machine)


def getParams(options=None):
    """return a string containing script parameters.

    Parameters are all variables that start with ``param_``.
    """
    result = []
    if options:
        members = options.__dict__
        for k, v in sorted(members.items()):
            result.append("# %-40s: %s" % (k, str(v).encode("string_escape")))
    else:
        vars = inspect.currentframe().f_back.f_locals
        for var in filter(lambda x: re.match("param_", x), vars.keys()):
            result.append("# %-40s: %s" %
                          (var, str(vars[var]).encode("string_escape")))

    if result:
        return "\n".join(result)
    else:
        return "# no parameters."


def getFooter():
    """return a header string with command line options and
    timestamp.
    """
    return "# job finished in %i seconds at %s -- %s -- %s" %\
           (time.time() - global_starting_time,
            time.asctime(time.localtime(time.time())),
            " ".join(map(lambda x: "%5.2f" % x, os.times()[:4])),
            global_id)


class MultiLineFormatter(logging.Formatter):

    '''logfile formatter: add identation for multi-line entries.'''

    def format(self, record):
        s = logging.Formatter.format(self, record)
        if s.startswith("#"):
            prefix = "#"
        else:
            prefix = ""
        if record.message:
            header, footer = s.split(record.message)
            s = prefix + s.replace('\n', '\n%s' % prefix + ' ' * len(header))
        return s


def Start(parser=None,
          argv=sys.argv,
          quiet=False,
          add_pipe_options=True,
          return_parser=False):
    """set up an experiment.

    The :py:func:`Start` method will set up a file logger and add some
    default and some optional options to the command line parser.  It
    will then parse the command line and set up input/output
    redirection and start a timer for benchmarking purposes.

    The default options added by this method are:

    ``-v/--verbose``
        the :term:`loglevel`

    ``timeit``
        turn on benchmarking information and save to file

    ``timeit-name``
         name to use for timing information,

    ``timeit-header``
         output header for timing information.

    ``seed``
         the random seed. If given, the python random
         number generator will be initialized with this
         seed.

    Optional options added are:

    Arguments
    ---------

    param parser : :py:class:`U.OptionParser`
       instance with command line options.

    argv : list
        command line options to parse. Defaults to
        :py:data:`sys.argv`

    quiet : bool
        set :term:`loglevel` to 0 - no logging

    return_parser : bool
        return the parser object, no parsing. Useful for inspecting
        the command line options of a script without running it.

    add_pipe_options : bool
        add common options for redirecting input/output

    Returns
    -------
    tuple
       (:py:class:`U.OptionParser` object, list of positional
       arguments)

    """

    if not parser:
        parser = OptionParser(
            version="%prog version: $Id$")

    global global_options, global_args, global_starting_time

    # save default values given by user
    user_defaults = copy.copy(parser.defaults)

    global_starting_time = time.time()

    group = OptionGroup(parser, "Script timing options")

    group.add_option("--timeit", dest='timeit_file', type="string",
                     help="store timeing information in file [%default].")
    group.add_option("--timeit-name", dest='timeit_name', type="string",
                     help="name in timing file for this class of jobs "
                     "[%default].")
    group.add_option("--timeit-header", dest='timeit_header',
                     action="store_true",
                     help="add header for timing information [%default].")
    parser.add_option_group(group)

    group = OptionGroup(parser, "Common options")

    group.add_option("--random-seed", dest='random_seed', type="int",
                     help="random seed to initialize number generator "
                     "with [%default].")

    group.add_option("-v", "--verbose", dest="loglevel", type="int",
                     help="loglevel [%default]. The higher, the more output.")

    group.add_option("-?", dest="short_help", action="callback",
                     callback=callbackShortHelp,
                     help="output short help (command line options only.")

    parser.add_option_group(group)

    if quiet:
        parser.set_defaults(loglevel=0)
    else:
        parser.set_defaults(loglevel=1)

    parser.set_defaults(
        timeit_file=None,
        timeit_name='all',
        timeit_header=None,
        random_seed=None,
    )

    if add_pipe_options:

        group.add_option("-I", "--stdin", dest="stdin", type="string",
                         help="file to read stdin from [default = stdin].",
                         metavar="FILE")
        group.add_option("-L", "--log", dest="stdlog", type="string",
                         help="file with logging information "
                         "[default = stdout].",
                         metavar="FILE")
        group.add_option("-E", "--error", dest="stderr", type="string",
                         help="file with error information "
                         "[default = stderr].",
                         metavar="FILE")
        group.add_option("-S", "--stdout", dest="stdout", type="string",
                         help="file where output is to go "
                         "[default = stdout].",
                         metavar="FILE")
        group.add_option("--log2stderr", dest="log2stderr",
                         action="store_true", help="send logging information"
                         " to stderr [default = False].")

        parser.set_defaults(stderr=sys.stderr)
        parser.set_defaults(stdout=sys.stdout)
        parser.set_defaults(stdlog=sys.stdout)
        parser.set_defaults(stdin=sys.stdin)
        parser.set_defaults(log2stderr=False)

    parser.add_option_group(group)

    # restore user defaults
    parser.defaults.update(user_defaults)

    if return_parser:
        return parser

    global_options, global_args = parser.parse_args(argv[1:])

    if global_options.random_seed is not None:
        random.seed(global_options.random_seed)

    if add_pipe_options:
        if global_options.stdout != sys.stdout:
            global_options.stdout = openFile(global_options.stdout, "w")
        if global_options.stderr != sys.stderr:
            if global_options.stderr == "stderr":
                global_options.stderr = global_options.stderr
            else:
                global_options.stderr = openFile(global_options.stderr, "w")
        if global_options.stdlog != sys.stdout:
            global_options.stdlog = openFile(global_options.stdlog, "a")
        elif global_options.log2stderr:
            global_options.stdlog = global_options.stderr
        if global_options.stdin != sys.stdin:
            global_options.stdin = openFile(global_options.stdin, "r")
    else:
        global_options.stderr = sys.stderr
        global_options.stdout = sys.stdout
        global_options.stdin = sys.stdin
        if global_options.log2stderr:
            global_options.stdlog = sys.stderr
        else:
            global_options.stdlog = sys.stdout

    if global_options.loglevel >= 1:
        global_options.stdlog.write(getHeader() + "\n")
        global_options.stdlog.write(getParams(global_options) + "\n")
        global_options.stdlog.flush()

    # configure logging
    # map from 0-10 to logging scale
    # 0: quiet
    # 1: little verbositiy
    # >1: increased verbosity
    if global_options.loglevel == 0:
        lvl = logging.ERROR
    elif global_options.loglevel == 1:
        lvl = logging.INFO
    else:
        lvl = logging.DEBUG

    if global_options.stdout == global_options.stdlog:
        format = '# %(asctime)s %(levelname)s %(message)s'
    else:
        format = '%(asctime)s %(levelname)s %(message)s'

    logging.basicConfig(
        level=lvl,
        format=format,
        stream=global_options.stdlog)

    # set up multi-line logging
    # Note that .handlers is not part of the API, might change
    # Solution is to configure handlers explicitely.
    for handler in logging.getLogger().handlers:
        handler.setFormatter(MultiLineFormatter(format))

    return global_options, global_args


def Stop():
    """stop the experiment.

    This method performs final book-keeping, closes the output streams
    and writes the final log messages indicating script completion.
    """

    if global_options.loglevel >= 1 and global_benchmark:
        t = time.time() - global_starting_time
        global_options.stdlog.write(
            "######### Time spent in benchmarked functions #########\n")
        global_options.stdlog.write("# function\tseconds\tpercent\n")
        for key, value in global_benchmark.items():
            global_options.stdlog.write(
                "# %s\t%6i\t%5.2f%%\n" % (key, value,
                                          (100.0 * float(value) / t)))
        global_options.stdlog.write(
            "#######################################################\n")

    if global_options.loglevel >= 1:
        global_options.stdlog.write(getFooter() + "\n")

    # close files
    if global_options.stdout != sys.stdout:
        global_options.stdout.close()
    # do not close log, otherwise error occurs in atext.py
    # if global_options.stdlog != sys.stdout:
    #   global_options.stdlog.close()

    if global_options.stderr != sys.stderr:
        global_options.stderr.close()

    if global_options.timeit_file:

        outfile = open(global_options.timeit_file, "a")

        if global_options.timeit_header:
            outfile.write("\t".join(
                ("name", "wall", "user", "sys", "cuser", "csys",
                 "host", "system", "release", "machine",
                 "start", "end", "path", "cmd")) + "\n")

        csystem, host, release, version, machine = map(str, os.uname())
        uusr, usys, c_usr, c_sys = map(lambda x: "%5.2f" % x, os.times()[:4])
        t_end = time.time()
        c_wall = "%5.2f" % (t_end - global_starting_time)

        if sys.argv[0] == "run.py":
            cmd = global_args[0]
            if len(global_args) > 1:
                cmd += " '" + "' '".join(global_args[1:]) + "'"
        else:
            cmd = sys.argv[0]

        result = "\t".join((global_options.timeit_name,
                            c_wall, uusr, usys, c_usr, c_sys,
                            host, csystem, release, machine,
                            time.asctime(time.localtime(global_starting_time)),
                            time.asctime(time.localtime(t_end)),
                            os.path.abspath(os.getcwd()),
                            cmd)) + "\n"

        outfile.write(result)
        outfile.close()


def log(loglevel, message):
    """log message at loglevel."""
    logging.log(loglevel, message)


def info(message):
    '''log information message, see the :mod:`logging` module'''
    logging.info(message)


def warning(message):
    '''log warning message, see the :mod:`logging` module'''
    logging.warning(message)


def warn(message):
    '''log warning message, see the :mod:`logging` module'''
    logging.warning(message)


def debug(message):
    '''log debugging message, see the :mod:`logging` module'''
    logging.debug(message)


def error(message):
    '''log error message, see the :mod:`logging` module'''
    logging.error(message)


def critical(message):
    '''log critical message, see the :mod:`logging` module'''
    logging.critical(message)
