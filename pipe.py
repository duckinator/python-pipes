#!/usr/bin/env python3

import shlex
from subprocess import Popen, PIPE
import sys

class CommandPipe:
    def __init__(self, stdin=None):
        self.stdin = stdin
        self.cmds = []

    def __truediv__(self, other):
        if isinstance(other, str):
            other = shlex.split(other)
        self.cmds.append(other)
        return self

    def __gt__(self, other):
        return self.run(*other)

    def _build_procs(self, cmds, stdout_, stderr_):
        procs = [
            Popen(cmds[0], stdin=self.stdin, stdout=PIPE, stderr=PIPE)
        ]

        last_and_cmd = zip(procs, cmds[1:])
        # TODO: Figure out why this needs to be [2:], not [1:].
        if self.stdin is None:
            last_and_cmd = zip(procs, cmds[2:])

        procs += [
            Popen(cmd, stdin=last.stdout, stdout=PIPE, stderr=PIPE) for (last, cmd) in last_and_cmd
        ]

        procs += [
            Popen(cmds[-1], stdin=procs[-1].stdout, stdout=stdout_, stderr=stderr_)
        ]

        # Allow proc[0] to receive SIGPIPE if procs[len(procs) - 1] exits.
        # TODO: Figure out if this is correct. I'm not sure I understand the rationale.
        procs[0].stdout.close()
        procs[0].stderr.close()

        return procs

    def run(self, stdout=PIPE, stderr=PIPE):
        procs = self._build_procs(self.cmds, stdout, stdout)
        return procs[-1].communicate()


pipe = CommandPipe

pipe(sys.stdin)             /\
        "sed s/foo/bar/"    /\
        "cut -d '{' -f 2"   /\
        "cat"               /\
        "cut -d '}' -f 1"   > (sys.stdout, sys.stderr)

#pipe() / "ls" / "cat" > (sys.stdout, sys.stderr)

pipe()                              /\
        "echo \"{'foobar':'eh?'}\"" /\
        "sed s/foo/bar/"            /\
        "cut -d '{' -f 2"           /\
        "cat"                       /\
        "cut -d '}' -f 1"           > (sys.stdout, sys.stderr)
