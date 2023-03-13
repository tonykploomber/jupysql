from IPython.core.magic_arguments import parse_argstring
from jinja2 import Template
import ipywidgets as widgets
from ipywidgets import interact

from sqlalchemy.engine import Engine

from sql import parse
from sql.store import store
from sql.connection import Connection


class SQLPlotCommand:
    def __init__(self, magic, line) -> None:
        self.args = parse_argstring(magic.execute, line)


class SQLCommand:
    """
    Encapsulates the parsing logic (arguments, SQL code, connection string, etc.)

    """

    def __init__(self, magic, user_ns, line, cell) -> None:
        # def update_user_ns(my_limit):
            # print ("user_ns", user_ns)
            # print ("key", key)
            # print ("Value", value)
            # user_ns["my_limit"] = my_limit
        def dynamic_user_namespace(my_limit):
            # print ("cloned_user_ns", cloned_user_ns)
            self.user_ns["my_limit"] = my_limit
            print ("update", self.user_ns["my_limit"])

        self.user_ns = user_ns
        self.args = parse.magic_args(magic.execute, line)
        # self.args.line (everything that appears after %sql/%%sql in the first line)
        # is splited in tokens (delimited by spaces), this checks if we have one arg
        one_arg = len(self.args.line) == 1

        if (
            one_arg
            and self.args.line[0] in user_ns
            and isinstance(user_ns[self.args.line[0]], Engine)
        ):
            line_for_command = []
            add_conn = True
        else:
            line_for_command = self.args.line
            add_conn = False

        if one_arg and self.args.line[0] in Connection.connections:
            line_for_command = []
            add_alias = True
        else:
            add_alias = False
        self.command_text = " ".join(line_for_command) + "\n" + cell

        if self.args.file:
            with open(self.args.file, "r") as infile:
                self.command_text = infile.read() + "\n" + self.command_text

        self.parsed = parse.parse(self.command_text, magic)

        cloned_user_ns = dict(user_ns)
        if self.args.interactive:
            # print ("self.args.interactive", self.args.interactive)
            # print ("Type", type(user_ns))
            # for key, value in self.args.interactive:
                # self.update_user_ns(cloned_user_ns, name, value)
                # cloned_user_ns[name] = value
                # interact(update_user_ns)
                # cloned_user_ns[name] = value
            # interact(update_user_ns)

        # interact
            interact(dynamic_user_namespace, my_limit = 5)

        self.parsed["sql_original"] = self.parsed["sql"] = self._var_expand(
            self.parsed["sql"], user_ns, magic
        )
        print ("self.parsed['sql']", self.parsed["sql"] )
        if add_conn:
            self.parsed["connection"] = user_ns[self.args.line[0]]

        if add_alias:
            self.parsed["connection"] = self.args.line[0]

        if self.args.with_:
            final = store.render(self.parsed["sql"], with_=self.args.with_)
            self.parsed["sql"] = str(final)

    @property
    def sql(self):
        """
        Returns the SQL query to execute, without any other options or arguments
        """
        return self.parsed["sql"]

    @property
    def sql_original(self):
        """
        Returns the raw SQL query. Might be different from `sql` if using --with
        """
        return self.parsed["sql_original"]

    @property
    def connection(self):
        """Returns the connection string"""
        return self.parsed["connection"]

    @property
    def result_var(self):
        """Returns the result_var"""
        return self.parsed["result_var"]

    def _var_expand(self, sql, user_ns, magic):
        sql = Template(sql).render(user_ns)
        print ("user_ns", user_ns)
        parsed_sql = magic.shell.var_expand(sql, depth=2)

        has_SQLAlchemy_var_expand = ":" in sql and any(
            (":" + ns_var_key in sql for ns_var_key in user_ns.keys())
        )
        # has_SQLAlchemy_var_expand: detect if using Sqlalchemy fashion - :a

        msg = (
            "Variable substitution with $var and {var} has been "
            "deprecated and will be removed in a future version. "
            "Use {{var}} instead. To remove this, see: "
            "https://jupysql.ploomber.io/en/latest/howto.html#ignore-deprecation-warnings"  # noqa
        )

        if parsed_sql != sql or has_SQLAlchemy_var_expand:
            warnings.warn(msg, FutureWarning)

        return parsed_sql
