
from IPython.display import display, HTML


class TestHistory:
    """
    This object is intended to store the test history and results for
    later being displayed on a Jupyter Notebook
    """

    def __init__(self):

        self.tests = {}

        return

    def add_test(self, tag, description, level, threshold=None):

        self.tests[tag] = {
                            'tag': tag,
                            'description': description,
                            'level': level,
                            'threshold': threshold,
                            'result': False
                           }

        # create hidden HTML Anchor
        # html = HTML(f"<a href='{tag.lower().replace('-', '')}' >{tag}</a>")  #

        # display the HTML object to put the link on the page:
        # display(html)

        return

    def set_test_result(self, tag, result):

        if tag in self.tests:
            self.tests[tag]['result'] = result

        return

    def show_tests(self, move_to_top=False):

        html = "<div id='validation_results'>\n"
        html += "   <h1>Validation Results</h1>\n"
        html += "   <table style='text-align:left;'>\n"
        html += "       <tr>\n"
        html += f"          <th>ID</th>\n"
        html += f"          <th>Description</th>\n"
        html += f"          <th>Level</th>\n"
        html += f"          <th>Threshold</th>\n"
        html += f"          <th>Result</th>\n"
        html += "       </tr>\n"

        for tag in self.tests:

            test = self.tests[tag]

            # html += HTML(f"<a href='#{tag.lower().replace('-', '')}'>{test['description']}</a>")

            css_style = "color:red;"
            if test['result']:
                css_style = "color:green;"

            html += f"       <tr style='{css_style}'>\n"
            html += f"          <td>{tag}</td>\n"
            html += f"          <td>{test['description']}</td>\n"
            html += f"          <td>{test['level']}</td>\n"

            if test['threshold']:
                html += f"          <td>{test['threshold']}</td>\n"
            else:
                html += f"          <td></td>\n"

            if test['result']:
                html += f"          <td>OK!</td>\n"
            else:
                html += f"          <td>FAIL!</td>\n"

            html += "       </tr>\n"

        html += "   </table>\n"
        html += "</div>\n"

        if move_to_top:
            #
            # Inserts Javascript and JQuery in the HTML page in order to obtain the validation
            # notes html div and insert it in the contents part of the cloned header element.
            # Later on this element is inserted after the header.
            #
            html += '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>\n'
            html += '<script>\n' \
                    '   var val_results = $("#validation_results");\n' \
                    '   var header = $(".notebook-container").find(".cell").first();\n' \
                    '   if ($("#notebook-container").length == 0) {\n' \
                    '       // Detect the machine who exported to HTML: \n' \
                    '       // Notebook exported to HTML by spice server \n' \
                    '       // returns different Html elements than ones got from local \n' \
                    '       header = $(".jp-Notebook").find(".jp-Cell-inputWrapper").first();\n' \
                    '   }\n' \
                    '   var containerDiv = header.clone();\n' \
                    '   containerDiv.children().last().html(val_results);\n' \
                    '   containerDiv.insertAfter(header);\n' \
                    '</script>\n'

        display(HTML(html))

        return

