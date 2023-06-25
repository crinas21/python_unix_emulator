class Directory:
    
    def __init__(self, fullname:str, owner:str):
        self.fullname = fullname
        self.owner = owner
        self.defaultPerms = ["d", "r", "w", "x", "r", "-", "x"]
        self.contents = []

    def get_fullname(self) -> str:
        return self.fullname

    def set_fullname(self, n:str):
        self.fullname = n

    def get_simplename(self) -> str:
        if self.fullname == "/":
            return "/"
        return self.fullname.split('/')[-1]

    def get_owner_name(self) -> str:
        return self.owner

    def set_owner(self, u:str):
        self.owner = u

    def get_contents(self) -> list:
        return self.contents

    def remove_content(self, content):
        self.contents.remove(content)

    def add_content(self, content):
        self.contents.append(content)

    def get_perms_usr(self, user:str) -> str:
        if user == self.owner:
            return self.defaultPerms[1:4]
        else:
            return self.defaultPerms[4:]

    def get_perms_str(self) -> str:
        return ''.join(self.defaultPerms)

    def chmod_perms(self, who:list, op:str, perms:list):
        if op == "+":
            for w in who:
                if w == "u" or w == "a":
                    if "r" in perms:
                        self.defaultPerms[1] = "r"
                    if "w" in perms:
                        self.defaultPerms[2] = "w"
                    if "x" in perms:
                        self.defaultPerms[3] = "x"
                if w == "o" or w == "a":
                    if "r" in perms:
                        self.defaultPerms[4] = "r"
                    if "w" in perms:
                        self.defaultPerms[5] = "w"
                    if "x" in perms:
                        self.defaultPerms[6] = "x"

        elif op == "-":
            for w in who:
                if w == "u" or w == "a":
                    if "r" in perms:
                        self.defaultPerms[1] = "-"
                    if "w" in perms:
                        self.defaultPerms[2] = "-"
                    if "x" in perms:
                        self.defaultPerms[3] = "-"
                if w == "o" or w == "a":
                    if "r" in perms:
                        self.defaultPerms[4] = "-"
                    if "w" in perms:
                        self.defaultPerms[5] = "-"
                    if "x" in perms:
                        self.defaultPerms[6] = "-"
                        
        elif op == "=":
            for w in who:
                if w == "u" or w == "a":
                    if "r" in perms:
                        self.defaultPerms[1] = "r"
                    else:
                        self.defaultPerms[1] = "-"
                    if "w" in perms:
                        self.defaultPerms[2] = "w"
                    else:
                        self.defaultPerms[2] = "-"
                    if "x" in perms:
                        self.defaultPerms[3] = "x"
                    else:
                        self.defaultPerms[3] = "-"
                if w == "o" or w == "a":
                    if "r" in perms:
                        self.defaultPerms[4] = "r"
                    else:
                        self.defaultPerms[4] = "-"
                    if "w" in perms:
                        self.defaultPerms[5] = "w"
                    else:
                        self.defaultPerms[5] = "-"
                    if "x" in perms:
                        self.defaultPerms[6] = "x"
                    else:
                        self.defaultPerms[6] = "-"
                    
    def chmod_recursively(self, who:list, op:str, perms:list, user:str):
        for content in self.contents:
            if user == content.get_owner_name() or user == "root":
                content.chmod_perms(who, op, perms)
            else:
                print("chmod: Operation not permitted")

            if isinstance(content, Directory):
                content.chmod_recursively(who, op, perms, user)

    def chown_recursively(self, user:str):
        for content in self.contents:
            content.set_owner(user)
            if isinstance(content, Directory):
                content.chown_recursively(user)