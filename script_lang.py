#TODO loops +++
#TODO load resources ++
#TODO blit resources ++
#TODO resource type +
#TODO functions definitions +
#TODO get var from arrays ++
#TODO scrape lists from INSIDE call function brackets +++

def removekey(d, key):
    if key == "all":
        return {}
    r = dict(d)
    del r[key]
    return r

class ScriptHandler:
    def  __init__(self, debug=False):
        self.variables = {}
        self.safe_functions = {}
        self.debug = debug
        self.execution = True

    def get_file(self, filename):
        self.file = open(filename)
        self.file = self.file.read()
        self.file = self.file.replace("\r\n", "\n")
        self.file = self.file.replace("\r", "\n")
        self.file = self.file.split(";\n")
    
    def check_if_string(self, s):
        try:
            line = int(s)
            return line
        except ValueError:
            return s

    def parse_file(self):
        for i in self.file:
            if self.debug:
                print(i)
            if not(self.execution):
                self.execution = True
                break
            self.parse_line(i)

    def parse_line(self, line_a):
        line = line_a.split(" ")
        if "#" in line[0].upper():
            pass
        if "BREAK" in line[0].upper():
            self.execution = False
            if self.debug:
                print("[WARNING] Broke execution!")
        if "IF" in line[0].upper():
            if line[1] in self.variables:
                is_it = line[3]
                try:
                    is_it = self.variables[is_it]
                except:
                    try:
                        is_it = self.check_if_string(is_it).replace("\"", "")
                    except:
                        is_it = self.check_if_string(is_it)
                if self.variables[line[1]] == is_it:
                    if line[5] in self.safe_functions:
                        start = ""
                        end = ""
                        for i in range(0, len(line)):
                            if "(" in line[i]:
                                start = i
                            if ")" in line[i]:
                                end = i
                        if start == end:
                            arguments = line[start]
                            arguments = arguments.replace("(", "")
                            arguments = arguments.replace(")", "")
                            try:
                                arguments = self.variables[arguments]
                            except:
                                try:
                                    arguments = self.check_if_string(arguments).replace("\"", "")
                                except:
                                    arguments = self.check_if_string(arguments)
                            self.safe_functions[line[5]](arguments)
                        else:
                            arguments = " ".join(line[start:end]).split("; ")
                            arguments[0] = arguments[0].replace("(", "")
                            arguments[-1] = arguments[-1].replace(")", "")
                            for i in range(0, len(arguments)):
                                try:
                                    arguments[i] = self.variables[arguments[i]]
                                except:
                                    try:
                                        arguments[i] = self.check_if_string(arguments[i]).replace("\"", "")
                                    except:
                                        arguments[i] = self.check_if_string(arguments[i])
                            self.safe_functions[line[5]](*arguments)
            else:
                print("[ERROR] %s not in variables" % line[1])
    
        if "GET" in line[0].upper():
            if line[0] in self.variables:
                print("[ERROR] Value error")
            if line[-1] in self.variables:
                print("[ERROR] Value error")
            if line[1] in self.safe_functions:
                start = ""
                end = ""
                for i in range(0, len(line)):
                    if "(" in line[i]:
                        start = i
                    if ")" in line[i]:
                        end = i
                if start == end:
                    arguments = line[start]
                    arguments = arguments.replace("(", "")
                    arguments = arguments.replace(")", "")
                    try:
                        arguments = self.variables[arguments]
                    except:
                        try:
                            arguments = self.check_if_string(arguments).replace("\"", "")
                        except:
                            arguments = self.check_if_string(arguments)
                    s = self.safe_functions[line[1]](arguments)
                    self.variables.update({line[-1]: s})
                else:
                    arguments = " ".join(line[start:end+1]).split("; ")
                    arguments[0] = arguments[0].replace("(", "")
                    arguments[-1] = arguments[-1].replace(")", "")
                    for i in range(0, len(arguments)):
                        try:
                            arguments[i] = self.variables[arguments[i]]
                        except:
                            try:
                                arguments[i] = self.check_if_string(arguments[i]).replace("\"", "")
                            except:
                                arguments[i] = self.check_if_string(arguments[i])
                    s = self.safe_functions[line[1]](*arguments)
                    self.variables.update({line[-1]: s})
        if "STRING" in line[0].upper():
            type_r = str
            self.variables.update({line[2]: type_r(line[4]).replace("\"", "")})
        if "INT" in line[0].upper():
            type_r = int
            self.variables.update({line[2]: type_r(line[4])})
        if "BOOL" in line[0].upper():
            type_r = bool
            self.variables.update({line[2]: type_r(line[4])})
        if "TUPLE" in line[0].upper():
            #TODO fix tuples
            type_r = tuple
            array = " ".join(line[4:]).split("; ")
            array[0] = array[0].replace("[", "")
            array[-1] = array[-1].replace("]", "")
            for i in range(0, len(array)):
                #check if in self.variables
                #check if string
                try:
                    array[i] = self.variables[array[i]]
                except:
                    try:
                        array[i] = self.check_if_string(array[i]).replace("\"", "")
                    except:
                        array[i] = self.check_if_string(array[i])
            self.variables.update({line[2]: type_r(array)})
        if "ARRAY" in line[0].upper():
            type_r = list
            array = " ".join(line[4:]).split("; ")
            array[0] = array[0].replace("[", "")
            array[-1] = array[-1].replace("]", "")
            for i in range(0, len(array)):
                #check if in self.variables
                #check if string
                try:
                    array[i] = self.variables[array[i]]
                except:
                    try:
                        array[i] = self.check_if_string(array[i]).replace("\"", "")
                    except:
                        array[i] = self.check_if_string(array[i])
            self.variables.update({line[2]: type_r(array)})
        if "DESTROY" in line[0].upper():
            if "ALL" in line[1].upper():
                self.variables = removekey(self.variables, line[1].lower())
            if line[1] in list(self.variables.keys()):
                self.variables = removekey(self.variables, line[1])
                if self.debug:
                    print("[WARNING] Removed variable %s" % line[1])
        if "EXECUTE" in line[0].upper():
            if line[1] in self.safe_functions:
                start = ""
                end = ""
                for i in range(0, len(line)):
                    if "(" in line[i]:
                        start = i
                    if ")" in line[i]:
                        end = i
                if start == end:
                    arguments = line[start]
                    arguments = arguments.replace("(", "")
                    arguments = arguments.replace(")", "")
                    try:
                        arguments = self.variables[arguments]
                    except:
                        try:
                            arguments = self.check_if_string(arguments).replace("\"", "")
                        except:
                            arguments = self.check_if_string(arguments)
                    try:
                        self.safe_functions[line[1]]()
                    except:
                        self.safe_functions[line[1]](arguments)

                else:
                    print(start, end)
                    arguments = " ".join(line[start:end+1])
                    print(arguments)
                    arguments = arguments.split("; ")
                    print(arguments)
                    arguments[0] = arguments[0].replace("(", "")
                    arguments[-1] = arguments[-1].replace(")", "")
                    print(arguments)
                    for i in range(0, len(arguments)):
                        try:
                            arguments[i] = self.variables[arguments[i]]
                            print(arguments[i])
                        except:
                            try:
                                arguments[i] = self.check_if_string(arguments[i]).replace("\"", "")
                            except:
                                arguments[i] = self.check_if_string(arguments[i])
                    self.safe_functions[line[1]](*arguments)

        else:
            pass
        #print(self.variables)

#s = ScriptHandler("data/event/001_test_event.script")
#s.parse_file()
    
            