#!/usr/bin/env python3
"""
Refactored GDB extension:
- Uses decorators to automatically register custom functions and commands.
- The list_all command will display all registered items with their command names,
  short description, and usage information (from their docstrings).
- All output is printed directly.
"""

import gdb
import os
import json
import inspect

print("")
print("#########################")
print("# Load gdb_extension.py #")
print("#########################")
print("")

# ---------------------------
# Decorators and registration mechanism
# ---------------------------
REGISTERED_GDB_FUNCTIONS = []
REGISTERED_GDB_COMMANDS = []


def register_gdb_function(cls):
    """Decorator: Automatically add gdb.Function subclasses to the registration list."""
    REGISTERED_GDB_FUNCTIONS.append(cls)
    return cls


def register_gdb_command(cls):
    """Decorator: Automatically add gdb.Command subclasses to the registration list."""
    REGISTERED_GDB_COMMANDS.append(cls)
    return cls

# ---------------------------
# Custom GDB Functions
# ---------------------------


@register_gdb_function
class ContainerOfFunction(gdb.Function):
    """Return container pointer given a member pointer, container type, and member name.

@Usage: container_of(member_ptr, "container_type", "member_name")
    """

    def __init__(self):
        super(ContainerOfFunction, self).__init__("container_of")

    def invoke(self, *args):
        if len(args) != 3:
            raise gdb.GdbError("container_of takes exactly three arguments")
        member_ptr = args[0]
        container_type_str = (
            args[1].string() if args[1].type.code == gdb.TYPE_CODE_ARRAY else str(args[1]))
        member_name = (args[2].string() if args[2].type.code ==
                       gdb.TYPE_CODE_ARRAY else str(args[2]))
        try:
            container_type = gdb.lookup_type(container_type_str)
        except Exception as e:
            raise gdb.GdbError("Error looking up container type: " + str(e))
        offset = None
        for field in container_type.fields():
            if field.name == member_name:
                offset = field.bitpos // 8
                break
        if offset is None:
            raise gdb.GdbError("Member '%s' not found in type '%s'" %
                               (member_name, container_type_str))
        container_addr = int(member_ptr) - offset
        return gdb.Value(container_addr).cast(container_type.pointer())


@register_gdb_function
class PrintAllElementFunction(gdb.Function):

    """Return a string representing the 'value' of each element in a queue.

    Usage: print_all_element(queue_head)
    Example: print_all_element(my_queue)

    Assumes a circular doubly linked list of element_t, where each element_t
    has a 'value' field (char*) and a 'list' field. Up to 100 elements are printed.
    If more exist, "..." is appended.
    """

    def __init__(self):
        self.cmd_name = "print_all_element"
        super(PrintAllElementFunction, self).__init__(self.cmd_name)

    def invoke(self, args):
        if len(args) != 1:
            raise gdb.GdbError("print_all_element takes exactly one argument")
        head = args[0]
        try:
            element_type = gdb.lookup_type("element_t")
        except Exception as e:
            raise gdb.GdbError("Error looking up type element_t: " + str(e))
        offset = None
        for field in element_type.fields():
            if field.name == "list":
                offset = field.bitpos // 8
                break
        if offset is None:
            raise gdb.GdbError("Field 'list' not found in type element_t")
        result = ""
        count = 0
        max_count = 100
        try:
            current = head["next"]
        except Exception as e:
            raise gdb.GdbError("Error accessing head->next: " + str(e))
        while int(current) != int(head):
            if count >= max_count:
                result += "...\n"
                break
            try:
                current_int = int(current)
                element_addr = current_int - offset
                element_ptr = gdb.Value(element_addr).cast(
                    element_type.pointer())
                value_field = element_ptr.dereference()["value"]
                result += str(value_field) + "\n"
            except Exception as e:
                result += "Error processing element: " + str(e) + "\n"
                break
            try:
                current = current["next"]
            except Exception as e:
                result += "Error accessing next pointer: " + str(e) + "\n"
                break
            count += 1
        return result

# ---------------------------
# Custom GDB Commands
# ---------------------------


@register_gdb_command
class MyRegisterCommand(gdb.Command):
    """Custom command to print a message.

    Usage: my_register
    Example: my_register
    """

    def __init__(self):
        self.cmd_name = "my_register"
        super(MyRegisterCommand, self).__init__(
            self.cmd_name, gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        print("I'm registered function")


@register_gdb_command
class HandleSignalCommand(gdb.Command):
    """Custom command to configure signal handling.

    Usage: handle_signal <signal_name> <action>
    Example: handle_signal SIGINT ignore
    """

    def __init__(self):
        self.cmd_name = "handle_signal"
        super(HandleSignalCommand, self).__init__(
            self.cmd_name, gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        args = gdb.string_to_argv(arg)
        if len(args) < 2:
            print("Usage: handle_signal <signal_name> <action>")
            return
        signal_name = args[0]
        action = args[1]
        cmd = f"handle {signal_name} {action}"
        try:
            gdb.execute(cmd)
            print(f"Set handling for {signal_name} with action: {action}")
        except Exception as e:
            print("Error executing handle command:", e)


@register_gdb_command
class ListAllCommand(gdb.Command):
    """List all available custom functions and commands.

    @Usage: list_all
    """

    def __init__(self):
        self.cmd_name = "list_all"
        super(ListAllCommand, self).__init__(self.cmd_name, gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        prefix_cmd = "- "             # Prefix for the command name line
        prefix_brief = "    @Brief: "    # Prefix for the brief description line
        prefix_usage = "    @Usage: "    # Prefix for the usage line

        output = ""
        # Define groups: each group is a tuple with a header and the registry list.
        groups = [
            ("Available custom functions", REGISTERED_GDB_FUNCTIONS),
            ("Available custom commands", REGISTERED_GDB_COMMANDS)
        ]
        for header, registry in groups:
            output += "\n" + header + ":\n"
            for cls in registry:
                # Retrieve command name from instance if available; else, use class name.
                instance = getattr(cls, "_instance", None)
                cmd_name = instance.cmd_name if instance and hasattr(
                    instance, "cmd_name") else cls.__name__
                doc = inspect.cleandoc(cls.__doc__ or "")
                lines = doc.splitlines()
                brief = lines[0] if lines else ""
                usage = ""
                for line in lines:
                    if line.startswith("Usage:"):
                        usage = line[len("Usage:"):].strip()
                        break
                output += f"{prefix_cmd}`{cmd_name}`\n"
                output += f"{prefix_brief}{brief}\n"
                if usage:
                    output += f"{prefix_usage}{usage}\n"
        print(output)


# ---------------------------
# Auto-registration
# ---------------------------


def auto_register_extensions():
    # Automatically instantiate all custom GDB functions and commands and store the instance in the class.
    for cls in REGISTERED_GDB_FUNCTIONS:
        instance = cls()  # calls gdb.Function.__init__
        cls._instance = instance
    for cls in REGISTERED_GDB_COMMANDS:
        instance = cls()  # calls gdb.Command.__init__
        cls._instance = instance


def register_custom_extensions():
    auto_register_extensions()
    print("Custom GDB functions and commands registered.")
    setup_cmds_env = os.environ.get("GDB_SETUP_CMDS", "")
    if setup_cmds_env:
        try:
            setup_cmds = json.loads(setup_cmds_env)
            print(f"Using setup commands from environment: {setup_cmds}")
        except Exception as e:
            print("Error parsing GDB_SETUP_CMDS environment variable:", e)
            setup_cmds = []
        for cmd in setup_cmds:
            try:
                gdb.execute(cmd)
                print(f"Executed setup command: {cmd}")
            except Exception as e:
                print(f"Error executing setup command '{cmd}':", e)
        print("Setup commands executed")
    else:
        print("No setup commands required")


# When this script is loaded by GDB, immediately register the custom extensions
register_custom_extensions()
gdb.execute("list_all")

print("")
print("#########################")
print("# Exit gdb_extension.py #")
print("#########################")
print("")
