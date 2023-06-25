# python_unix_emulator
Python program that is capable of creating a virtual namespace through simulated Unix commands.

# High Level Capabilities
- Interpret commands received on standard input.
- Produce messages on standard output.
- Maintain some data structure that keeps track of a virtual name space.
- Create, delete and move virtual files and folders during program run time.
- Support user and permission management in addition to file management.

# Commands
## exit
- Quit the program.

## pwd
- Print the name of current working virtual directory.

## cd \<dir>
- Change the working directory to \<dir>.
- Require current effective user's execute bit x on \<dir> and on \<dir>'s ancestors.

## mkdir [-p] \<dir>
- Create the directory \<dir> if doesn't exist.
- Require current effecetive user's execute bit x on \<dir>'s ancestors.
- Require current effective user's write bit w on \<dir>'s parent.
- Directories are created with drwxr-x permission with regards to the current effective user.

## touch \<file>
- Create the file \<file> if doesn't exist.
- Require current effective user's execute bit x on \<file>'s ancestors.
- Require current effective user's write bit w on \<file>'s parent.
- Files are created with -rw-r-- permission with regards to the current effective user.

## cp \<src> \<dst>
- Copy a file \<src> to a file \<dst>
- Require current effective user's read bit r on \<src>.
- Require current effective user's execute bit x on \<src>'s and \<dst>'s ancestors.
- Require current effective user's write bit w on \<dst>'s parent.

## mv \<src> \<dst>
- Move a file \<src> to a file \<dst>.
- Require current effective user's execute bit x on \<src>'s and \<dst>'s ancestors.
- Require current effective user's write bit w on \<src>'s and \<dst>'s parent.

## rm \<path>
- Remove the file at \<path>
- Require current effective user's write bit w on \<path>.
- Require current effective user's execute bit x on \<path>'s ancestors.
- Require current effective user's write bit w on \<path>'s parent.

## rmdir \<dir>
- Remove empty directory
- Require current effective user's exceute bit x on \<dir>'s ancestors.
- Require current effectuve user's write bit w on \<dir>'s parent.

## chmod [-r] \<s> \<path>
- Change file mode bits
- Require current effective user to be either the owner of \<path> or root.
- Require current effective user's execute bit x of \<path>'s ancestors.
- If the current effective user is nether the owner of \<path> nor root, operation is not permitted.
- -r changes mode of files and directories at \<path> recursively.

## chown [-r] \<user> \<path>
- Change file owner.
- Only allowed by root.

## adduser \<user>
- Add a user to the system.
- Only allowed by root.

## deluser \<user>
- Remove a user from the system.
- Only allowed by root.

## su [user]
- Switch the current effective user to \<user>
- Switch to root if \<user> omitted.

## ls [-a] [-d] [-l] [path]
- List information about \<path>. Sort entries alphabetically.
- Require current effective user's read bit r on \<path>.
- Require current effective ucer's read bit r on \<path>'s parent if \<path> is a valid file or -d is specified.
- Require current effective user's execute bit x on \<path>'s ancestors.

# A Note on Errors
- The program will never crash as all invalid inputs are accounted for.
- For any invalid inputs (e.g. invalid commands, referring to non-existent files/directories/users operations trying to be done without necessary permissions) an appropriate error message will be displayed.
