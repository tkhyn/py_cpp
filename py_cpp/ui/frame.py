from py_cpp import maths

from . import wxpy_cpp_ui


class MainFrame(wxpy_cpp_ui.MainFrame):

    def on_input_change(self, event):
        """
        Handling operand / operator change events
        """

        # parsing values
        values = []
        for name in ['a', 'b']:
            field = getattr(self, '%s_input' % name)
            try:
                value = int(field.GetValue())
            except ValueError:
                value = 0
            values.append(value)

        # calculating result
        operator = self.operator.GetString(self.operator.GetSelection())
        result = getattr(maths, 'add' if operator == '+' else 'sub')(*values)
        self.result.SetValue(str(result))
