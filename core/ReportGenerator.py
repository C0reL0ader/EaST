import os
import time
class ReportGenerator:
    def __init__(self):
        self.path_to_templates = os.getcwd() + "/data/report_templates/"
        self.start_date_time = time.strftime("%d %b %Y %H-%M-%S")
        self.succeeded_count = 0
        self.failed_count = 0
        self.categories = {}
        self.report_name = self.generate_report()

    def _generate_content(self, module):
        content = self.read_file_content(self.path_to_templates + "row_template.html")

        options = ""
        listener = ""
        if module["OPTIONS"]:
            options += "<div class=\"entry\">Module options:</div>"
            for option, value in module["OPTIONS"].iteritems():
                if option == "listener":
                    listener += "<div class=\"entry\">Listener enabled with options:</div>"
                    for l_option, l_value in module["OPTIONS"]["listener"].iteritems():
                        listener += "{option}: {value}".format(option=l_option, value=l_value)
                    listener += "<br>"
                    continue
                options += "{option}: {value}".format(option=option, value=value)
                options += "<br>"


        content = content.format(MODULE_NAME=str(module["NAME"]),
                       DESCRIPTION=str(module["DESCRIPTION"]),
                       NOTES=str(module["NOTES"]),
                       LOG=("<br>".join(m.time + ":" + m.message for m in module["LOG"])).encode('utf-8'),
                       IS_SHELL_CONNECTED=str(module["IS_SHELL_CONNECTED"]),
                       CVE=str(module["CVE"]),
                       CLASS="succeeded" if module["RESULT"] else "failed",
                       IS_SUCCESS="Succeeded" if module["RESULT"] else "Failed",
                       OPTIONS=str(options),
                       LISTENER=str(listener))

        if module["RESULT"]:
            self.succeeded_count += 1
        else:
            self.failed_count += 1
        category = module["PATH"].replace("/", "").capitalize()
        if category in self.categories:
            self.categories[category].append(content)
        else:
            self.categories[category] = [content]

    def append_module(self, module):
        self._generate_content(module)
        self._rewrite_report()

    def generate_report(self):
        path = os.getcwd() + "/Reports"
        if not os.path.exists(path):
            os.mkdir(path)
        name = path + "/" + self.start_date_time + ".html"
        with open(name, "w") as f:
            f.write("")
        return name

    def read_file_content(self, filename):
        content = ""
        with open(filename, 'r') as f:
            content = f.read()
        return content

    def _rewrite_report(self):
        contents= ""
        index = 1
        for category_name in self.categories.keys():
            contents += "<div class='categoryName'>{}.) <a href='#{}'>{}</a></div>".format(index, category_name.lower(), category_name)
            index += 1
        contents += "<br>"
        for category_name, category in self.categories.iteritems():
            contents += "<div id='"+ category_name.lower()+"'><div class='categoryName'>"+ category_name + "(" + str(len(category)) + ")" + "</div>"
            contents += "\n".join(category)
            contents += "</div>"
        common = self.read_file_content(self.path_to_templates + "common.html")
        with open(self.report_name, 'w') as f:
            f.write(common % (self.start_date_time, self.succeeded_count, self.failed_count, contents))
