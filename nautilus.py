from directory import Directory
from file import File

def find_flags(line:list) -> list:
    '''Returns a list of all flags from the command line'''
    flags = []
    i = 0
    while i < len(line):
        if line[i][0] == "-" and len(line[i]) > 1:
            flags.append(line[i])
            line.remove(line[i])
        else:
            break
    return flags


def invalid_flags(flags:list, valid_flags:list) -> bool:
    '''
    Returns a boolean True if flags given as command line
    arguments are not acceptable, else False
    '''
    for flag in flags:
        if not flag in valid_flags:
            return True
    return False


def invalid_char(args:list) -> bool:
    '''
    Returns a boolean True if arguments contain
    invalid characters, else False
    '''
    valid_char_list = [" ", "-", ".", "_", "/"]
    for arg in args:
        for ch in arg:
            if not ch.isalnum() and not ch in valid_char_list:
                return True
    return False


def get_abs_path(rel_path:str, cwd:str) -> str:
    '''Returns the absolute path of a given path, accounting for dots'''
    if rel_path[0] != "/":
        if cwd == "/":
            abs_path = cwd + rel_path
        else:
            abs_path = cwd + "/" + rel_path
    else:
        abs_path = rel_path

    abs_path = abs_path.split("/")
    i = 0
    while i < len(abs_path):
        if abs_path[i] == ".":
            abs_path.pop(i)
            i -= 1
        elif abs_path[i] == "..":
            abs_path.pop(i)
            if i != 1:
                abs_path.pop(i-1)
                i -= 2
            else:
                i -= 1
        i += 1
    
    if len(abs_path) == 1:
        abs_path = "/"
    else:
        abs_path = '/'.join(abs_path)

    return abs_path


def find_leading_paths(path:str) -> list:
    '''
    Returns a list of all of the leading
    absolute paths to a specified path
    '''
    path_names = path.strip("/").split("/")
    leading_paths = []
    i = 0
    while i < len(path_names)-1:
        l_path = ''
        j = 0
        while j <= i:
            l_path += "/" + path_names[j]
            j += 1
        leading_paths.append(l_path)
        i += 1
    leading_paths.insert(0, '/')
    return leading_paths


def find_ancestors_exist(dirDict:dict, ancestor_paths:list) -> bool:
    '''Returns a boolean True if all ancestor_paths exist, else False'''
    for path in ancestor_paths:
        if not path in dirDict:
            return False
    return True        


def find_all_executable(dirDict:dict, dir_paths:list, user:str) -> bool:
    '''
    Returns a boolean true if all directories in a list
    are executable by a certain user, else False
    '''
    for path in dir_paths:
        if dirDict.get(path).get_perms_usr(user)[2] != "x":
            return False
    return True


def rm_path(dirDict:dict, fileDict:dict, path:str, path_parent:str):
    '''Removes a specified path'''
    if path in fileDict:
        dirDict.get(path_parent).remove_content(fileDict.get(path))
        del fileDict[path]
    elif path in dirDict:
        dirDict.get(path_parent).remove_content(dirDict.get(path))
        del dirDict[path]


def main():
    usrLs = ["root"]
    usr = "root"

    dirDict = {
        "/": Directory("/", usr),
    }
    cwd = "/"

    fileDict = {}

    while True:
        line_str = input(f"{usr}:{cwd}$ ").strip()
        line = line_str.split()
        if line == []:
            continue
        cmd = line[0]
        line.pop(0)
        flags = find_flags(line)
        args = line

        # Put all items of the line enclosed in double quotes as one item
        i = 0
        start_joining = False
        while i < len(args):
            if args[i][0] == '"' and not start_joining:
                first_to_join = i
                start_joining = True
            if args[i][-1] == '"' and start_joining:
                args[first_to_join] = args[first_to_join][1:]
                args[i] = args[i][:-1]
                args[first_to_join:i+1] = [' '.join(args[first_to_join:i+1])]
                start_joining = False
                i = first_to_join
            i += 1


        if cmd == "exit":
            if len(args) != 0 or invalid_char(args) or flags != []:
                print("exit: Invalid syntax")
                continue
            print(f"bye, {usr}")
            exit()


        elif cmd == "pwd":
            if len(args) != 0 or invalid_char(args) or flags != []:
                print("pwd: Invalid syntax")
                continue
            print(cwd)


        elif cmd == "cd":
            if len(args) != 1 or invalid_char(args) or flags != []:
                print("cd: Invalid syntax")
                continue

            dr_path = get_abs_path(args[0], cwd)

            if not dr_path in dirDict and not dr_path in fileDict:
                print("cd: No such file or directory")
            elif dr_path in fileDict:
                print("cd: Destination is a file")
            elif dr_path in dirDict:
                if dirDict.get(dr_path).get_perms_usr(usr)[2] == "x" \
                or usr == "root":
                    cwd = dr_path
                else:
                    print("cd: Permission denied")


        elif cmd == "mkdir":
            if len(args) != 1 or invalid_char(args) \
            or invalid_flags(flags, ["-p"]):
                print("mkdir: Invalid syntax")
                continue
            
            dr_path = get_abs_path(args[0].rstrip("/"), cwd)

            if not "-p" in flags:
                dr_ancestors = find_leading_paths(dr_path)
                dr_ancestors_exist = find_ancestors_exist(dirDict, dr_ancestors)

                if dr_path in dirDict or dr_path in fileDict:
                    print("mkdir: File exists")
                elif not dr_ancestors_exist:
                    print("mkdir: Ancestor directory does not exist")
                else:
                    dr_ancestors_executable = find_all_executable(dirDict, dr_ancestors, usr)
                    dr_parent_writable = (dirDict.get(dr_ancestors[-1]).get_perms_usr(usr)[1] == "w")

                    if (dr_ancestors_executable and dr_parent_writable) or usr == "root":
                        dirDict.update({dr_path: Directory(dr_path, usr)})
                        dirDict.get(dr_ancestors[-1]).add_content(dirDict.get(dr_path))
                    else:
                        print("mkdir: Permission denied")

            elif "-p" in flags:
                dr_ancestors = find_leading_paths(dr_path)
                drs_not_existing = []
                i = 0
                while i < len(dr_ancestors): # Find the earliest path that does not exist yet
                    if not dr_ancestors[i] in dirDict:
                        drs_not_existing = dr_ancestors[i:]
                        wd_to_add_to = dr_ancestors[i-1]
                        break
                    i += 1
                    if i == len(dr_ancestors):
                        wd_to_add_to = dr_ancestors[-1]
                if not dr_path in dirDict:
                    drs_not_existing.append(dr_path)

                dr_ancestors_executable = find_all_executable(dirDict, dr_ancestors[0:i], usr)
                dr_parent_writable = (dirDict.get(wd_to_add_to).get_perms_usr(usr)[1] == "w")

                if not (dr_ancestors_executable and dr_parent_writable) and usr != "root":
                    print("mkdir: Permission denied")
                else:
                    for dr in drs_not_existing:
                        dirDict.update({dr: Directory(dr, usr)})
                        dirDict.get(wd_to_add_to).add_content(dirDict.get(dr))
                        wd_to_add_to = dr


        elif cmd == "touch":
            if len(args) != 1 or invalid_char(args) or flags != []:
                print("touch: Invalid syntax")
                continue

            fl_path = get_abs_path(args[0], cwd)
            fl_ancestors = find_leading_paths(fl_path)
            fl_ancestors_exist = find_ancestors_exist(dirDict, fl_ancestors)

            if not fl_ancestors_exist:
                print("touch: Ancestor directory does not exist")
            elif not fl_path in fileDict and not fl_path in dirDict:
                fl_ancestors_executable = find_all_executable(dirDict, fl_ancestors, usr)
                fl_parent_writable = (dirDict.get(fl_ancestors[-1]).get_perms_usr(usr)[1] == "w")

                if (fl_ancestors_executable and fl_parent_writable) or usr == "root":
                    fileDict.update({fl_path: File(fl_path, usr)})
                    dirDict.get(fl_ancestors[-1]).add_content(fileDict.get(fl_path))
                else:
                    print("touch: Permission denied")


        elif cmd == "cp" or cmd == "mv":
            if len(args) != 2 or invalid_char(args) or flags != []:
                print(f"{cmd}: Invalid syntax")
                continue

            src = get_abs_path(args[0], cwd)
            src_ancestors = find_leading_paths(src)
            dst = get_abs_path(args[1], cwd)
            dst_ancestors = find_leading_paths(dst)

            if dst in fileDict or src == dst:
                print(f"{cmd}: File exists")
            elif dst in dirDict:
                print(f"{cmd}: Destination is a directory")
            elif src in dirDict:
                print(f"{cmd}: Source is a directory")
            elif not src in fileDict:
                print(f"{cmd}: No such file")
            elif not find_ancestors_exist(dirDict, dst_ancestors):
                print(f"{cmd}: No such file or directory")
            else:
                src_readable = (fileDict.get(src).get_perms_usr(usr)[0] == "r")
                src_ancestors_executable = find_all_executable(dirDict, src_ancestors, usr)
                dst_ancestors_executable = find_all_executable(dirDict, dst_ancestors, usr)
                src_parent_writable =  (dirDict.get(src_ancestors[-1]).get_perms_usr(usr)[1] == "w")
                dst_parent_writable = (dirDict.get(dst_ancestors[-1]).get_perms_usr(usr)[1] == "w")

                if cmd == "cp":
                    if src_readable and src_ancestors_executable and dst_ancestors_executable and dst_parent_writable or usr == "root":
                        fileDict.update({dst: File(dst, usr)})
                        dirDict.get(dst_ancestors[-1]).add_content(fileDict.get(dst))
                    else:
                        print("cp: Permission denied")

                elif cmd == "mv":
                    if src_ancestors_executable and src_parent_writable and dst_ancestors_executable and dst_parent_writable or usr == "root":
                        fileDict.update({dst: File(dst, usr)})
                        dirDict.get(dst_ancestors[-1]).add_content(fileDict.get(dst))
                        rm_path(dirDict, fileDict, src, src_ancestors[-1])
                    else:
                        print("mv: Permission denied")


        elif cmd == "rm":
            if len(args) != 1 or invalid_char(args) or flags != []:
                print("rm: Invalid syntax")
                continue

            path = get_abs_path(args[0], cwd)
            if not path in fileDict:
                if not path in dirDict:
                    print("rm: No such file")
                elif path in dirDict:
                    print("rm: Is a directory")
                continue

            path_ancestors = find_leading_paths(path)
            path_writable = (fileDict.get(path).get_perms_usr(usr)[1] == "w")
            path_ancestors_executable = find_all_executable(dirDict, path_ancestors, usr)
            path_parent_writable = (dirDict.get(path_ancestors[-1]).get_perms_usr(usr)[1] == "w")

            if path_writable and path_ancestors_executable and path_parent_writable or usr == "root":
                rm_path(dirDict, fileDict, path, path_ancestors[-1])
            else:
                print("rm: Permission denied")


        elif cmd == "rmdir":
            if len(args) != 1 or invalid_char(args) or flags != []:
                print("rmdir: Invalid syntax")
                continue

            dr_path = get_abs_path(args[0], cwd)
            dr_ancestors = find_leading_paths(dr_path)
            if not dr_path in dirDict and not dr_path in fileDict:
                print("rmdir: No such file or directory")
            elif not dr_path in dirDict:
                print("rmdir: Not a directory")
            elif dirDict.get(dr_path).get_contents() != []:
                print("rmdir: Directory not empty")
            elif dirDict.get(dr_path).get_contents() != []:
                print("rmdir: Directory not empty")
            elif dr_path == cwd:
                print("rmdir: Cannot remove pwd")
            else:
                dr_ancestors_executable = find_all_executable(dirDict, dr_ancestors, usr)
                dr_parent_writable = (dirDict.get(dr_ancestors[-1]).get_perms_usr(usr)[1] == "w")
                if dr_ancestors_executable and dr_parent_writable:
                    rm_path(dirDict, fileDict, dr_path, dr_ancestors[-1])
                else:
                    print("rmdir: Permission denied")


        elif cmd == "chmod":
            if len(args) != 2 or invalid_flags(flags, ["-r"]) or invalid_char(args[1:]):
                print("chmod: Invalid syntax")
                continue

            s = list(args[0])
            path = args[1]

            path = get_abs_path(path, cwd)
            path_ancestors = find_leading_paths(path)
            if path in fileDict:
                owner = fileDict.get(path).get_owner_name()
            elif path in dirDict:
                owner = dirDict.get(path).get_owner_name()
            else:
                owner = None

            op_count = 0
            invalid_mode = False
            for i in s: # Find the operator and if there is more than one
                if i == "+" or i == "-" or i == "=":
                    op = i
                    op_count += 1

            if op_count != 1:
                invalid_mode = True
            else:
                who = s[:s.index(op)]
                perms = s[s.index(op)+1:]
                for w in who:
                    if w != "u" and w != "o" and w != "a":
                        invalid_mode = True
                for p in perms:
                    if p != "r" and p != "w" and p != "x":
                        invalid_mode = True

            if invalid_mode:
                print("chmod: Invalid mode")
                continue
            elif usr != owner and usr != "root":
                print("chmod: Operation not permitted")
            elif not find_all_executable(dirDict, path_ancestors, usr):
                print("chmod: Permission denied")
                continue
            elif not path in fileDict and not path in dirDict:
                print("chmod: No such file or directory")
                continue

            if path in dirDict:
                if usr == owner or usr == "root":
                    dirDict.get(path).chmod_perms(who, op, perms)
                if "-r" in flags:
                    dirDict.get(path).chmod_recursively(who, op, perms, usr)
            elif path in fileDict:
                if usr == owner or usr == "root":
                    fileDict.get(path).chmod_perms(who, op, perms)


        elif cmd == "chown":
            if len(args) != 2 or invalid_char(args) or invalid_flags(flags, ["-r"]):
                print("chown: Invalid syntax")
                continue

            u = args[0]
            path = get_abs_path(args[1], cwd)

            if not u in usrLs:
                print("chown: Invalid user")
            elif not path in fileDict and not path in dirDict:
                print("chown: No such file or directory")
            elif usr != "root":
                print("chown: Operation not permitted")
            else:
                if path in dirDict:
                    dirDict.get(path).set_owner(u)
                    if "-r" in flags:
                        dirDict.get(path).chown_recursively(u)
                elif path in fileDict:
                    fileDict.get(path).set_owner(u)


        elif cmd == "adduser":
            if len(args) != 1 or invalid_char(args) or flags != []:
                print("adduser: Invalid syntax")
                continue

            u = args[0]

            if usr != "root":
                print("adduser: Operation not permitted")
            elif u in usrLs:
                print("adduser: The user already exists")
            else:
                usrLs.append(u)


        elif cmd == "deluser":
            if len(args) != 1 or invalid_char(args) or flags != []:
                print("deluser: Invalid syntax")
                continue

            u = args[0]

            if usr != "root":
                print("deluser: Operation not permitted")
            elif not u in usrLs:
                print("deluser: The user does not exist")
            elif u == "root":
                print("WARNING: You are just about to delete the root account")
                print("Usually this is never required as it may render the whole system unusable")
                print("If you really want this, call deluser with parameter --force")
                print("(but this `deluser` does not allow `--force`, haha)")
                print("Stopping now without having performed any action")
            else:
                usrLs.remove(u)


        elif cmd == "su":
            if len(args) > 1 or invalid_char(args) or flags != []:
                print("su: Invalid syntax")
                continue

            if len(args) == 0:
                u = "root"
            else:
                u = args[0]

            if not u in usrLs:
                print("su: Invalid user")
            else:
                usr = u


        elif cmd == "ls":
            if len(args) > 1 or invalid_char(args) or invalid_flags(flags, ["-a", "-d", "-l"]):
                print("ls: Invalid syntax")
                continue

            if len(args) == 1:
                path_given = True
                path = args[0]
            else:
                path_given = False
                path = cwd

            abs_path = get_abs_path(path, cwd)
            ancestors = find_leading_paths(abs_path)
            parent_path = ancestors[-1]

            if not abs_path in dirDict and not abs_path in fileDict:
                print("ls: No such file or directory")
                continue

            ancestors_executable = find_all_executable(dirDict, ancestors, usr)
            parent_readable = (dirDict.get(parent_path).get_perms_usr(usr)[0] == "r")
            if abs_path in dirDict:
                path_readable = (dirDict.get(abs_path).get_perms_usr(usr)[0] == "r")
            elif abs_path in fileDict:
                path_readable = (fileDict.get(abs_path).get_perms_usr(usr)[0] == "r")

            if "-d" in flags or abs_path in fileDict:
                if not (ancestors_executable and parent_readable) and usr != "root":
                    print("ls: Permission denied")
                else:
                    if abs_path in dirDict:
                        p = dirDict.get(abs_path)
                    elif abs_path in fileDict:
                        p = fileDict.get(abs_path)
                    
                    if not path_given:
                            path = "."

                    if not "-a" in flags and path[0] == ".":
                        continue
                    elif "-l" in flags:
                        print(p.get_perms_str(), p.get_owner_name(), path)
                    else:
                        print(path)

            elif abs_path in dirDict:
                if not (ancestors_executable and path_readable) and usr != "root":
                    print("ls: Permission denied")
                else:
                    items = []
                    for content in dirDict.get(abs_path).get_contents():
                        item_info = []
                        item_info.append(content.get_simplename())
                        item_info.append(content.get_owner_name())
                        item_info.append(content.get_perms_str())
                        items.append(item_info)
                    items.append([".", dirDict.get(abs_path).get_owner_name(), dirDict.get(abs_path).get_perms_str()])
                    items.append(["..", dirDict.get(parent_path).get_owner_name(), dirDict.get(parent_path).get_perms_str()])
                    items = sorted(items, key=lambda x:x[0]) # Sort alphabetically by the first item of each info list in items
                    
                    if flags == []:
                        for i in items:
                            if i[0][0] != ".":
                                print(i[0])

                    elif "-l" in flags:
                        if "-a" in flags: # -l and -a
                            for i in items:
                                print(i[2], i[1], i[0])
                        else: # Only -l
                            for i in items:
                                if i[0][0] != ".":
                                    print(i[2], i[1], i[0])

                    else: # Only -a
                        for i in items:
                            print(i[0])


        else:
            print(f"{cmd}: Command not found")


if __name__ == "__main__":
    main()