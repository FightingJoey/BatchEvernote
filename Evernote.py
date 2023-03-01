# -*- coding: utf-8 
import os
import json
import time
import sys

package_file = os.path.normpath(os.path.abspath(__file__))
package_path = os.path.dirname(package_file)
lib_path = os.path.join(package_path, "lib")

if lib_path not in sys.path:
    sys.path.append(lib_path)

import evernote.edam.type.ttypes as Types
from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.error.ttypes import EDAMErrorCode, EDAMUserException, EDAMSystemException, EDAMNotFoundException
import markdown2


ecode = EDAMErrorCode
error_groups = {
        'server': ('Internal server error', [ecode.UNKNOWN, ecode.INTERNAL_ERROR, ecode.SHARD_UNAVAILABLE, ecode.UNSUPPORTED_OPERATION ]),
        'data': ('User supplied data is invalid or conflicting', [ecode.BAD_DATA_FORMAT, ecode.DATA_REQUIRED, ecode.DATA_CONFLICT, ecode.LEN_TOO_SHORT, ecode.LEN_TOO_LONG, ecode.TOO_FEW, ecode.TOO_MANY]),
        'permission': ('Action not allowed, permission denied or limits exceeded', [ecode.PERMISSION_DENIED, ecode.LIMIT_REACHED, ecode.QUOTA_REACHED, ecode.TAKEN_DOWN, ecode.RATE_LIMIT_REACHED]),
        'auth': ('Authorisation error, consider re-configuring the plugin', [ecode.INVALID_AUTH, ecode.AUTH_EXPIRED]),
        'contents': ('Illegal note contents', [ecode.ENML_VALIDATION])
    }


def errcode2name(err):
    name = ecode._VALUES_TO_NAMES.get(err.errorCode, "UNKNOWN")
    name = name.replace("_", " ").capitalize()
    return name


def err_reason(err):
    for reason, group in error_groups.values():
        if err.errorCode in group:
            return reason
    return "Unknown reason"


def explain_error(err):
    if isinstance(err, EDAMUserException):
        print("Evernote error: [%s]\n\t%s" % (errcode2name(err), err.parameter))
        if err.errorCode in error_groups["contents"][1]:
            explanation = "The contents of the note are not valid.\n"
            msg = err.parameter.split('"')
            what = msg[0].strip().lower()
            if what == "element type":
                return explanation +\
                    "The inline HTML tag '%s' is not allowed in Evernote notes." %\
                    msg[1]
            elif what == "attribute":
                if msg[1] == "class":
                    return explanation +\
                        "The note contains a '%s' HTML tag "\
                        "with a 'class' attribute; this is not allowed in a note.\n"\
                        "Please use inline 'style' attributes or customise "\
                        "the 'inline_css' setting." %\
                        msg[3]
                else:
                    return explanation +\
                        "The note contains a '%s' HTML tag"\
                        " with a '%s' attribute; this is not allowed in a note." %\
                        (msg[3], msg[1])
            return explanation + err.parameter
        else:
            return err_reason(err)
    elif isinstance(err, EDAMSystemException):
        print("Evernote error: [%s]\n\t%s" % (errcode2name(err), err.message))
        return "Evernote cannot perform the requested action:\n" + err_reason(err)
    elif isinstance(err, EDAMNotFoundException):
        print("Evernote error: [%s = %s]\n\tNot found" % (err.identifier, err.key))
        return "Cannot find %s" % err.identifier.split('.', 1)[0]
    elif isinstance(err, gaierror):
        print("Evernote error: [socket]\n\t%s" % str(err))
        return 'The Evernote services seem unreachable.\n'\
               'Please check your connection and retry.'
    else:
        print("Evernote plugin error: %s" % str(err))
        return 'Evernote plugin error, please see the console for more details.\nThen contact developer at\n'\
               'https://github.com/bordaigorl/sublime-evernote/issues'



class EverNoteManager():
    _noteStore = None
    _notebook_by_guid = None
    _notebook_by_name = None
    _notebooks_cache = None

    def __init__(self, token, sandbox=False):
        self.dev_token = token
        self.client = EvernoteClient(token=self.dev_token, sandbox=sandbox, china=True)
        self.userStore = self.client.get_user_store()
        self.user = self.userStore.getUser()
        self.noteStore = self.client.get_note_store()
        self.extras = self.getExtras()
        self.notes = []

        wrapper_style = ''
        if 'inline-css' in self.extras:
            wrapper_style = self.extras['inline-css'].get('body', "")
            if len(wrapper_style) > 0:
                wrapper_style = ' style="%s"' % wrapper_style
        self.style = wrapper_style

        self.getLastUploadtime()

    # 获取上次上传笔记的时间
    def getLastUploadtime(self):
        time_path = os.path.join(os.getcwd(), '.time')
        infile = open(time_path,'r')
        contents = infile.read()
        infile.close()
        self.lastUploadTime = float(contents.replace('\n', ''))

    # 设置当前上传笔记的时间
    def setUploadtime(self):
        time_path = os.path.join(os.getcwd(), '.time')
        with open(time_path,'w') as f:
            f.write(str(time.time()))

    # 获取扩展信息
    def getExtras(self):
        from pygmstyles.github import GithubStyle

        MD_EXTRAS = {
            'fenced-code-blocks' : {'noclasses': True, 'cssclass': "", 'style': "default"}, 
            'cuddled-lists': None, 
            'tables': None, 
            'inline-css': {'tr:even': 'border: 1px solid #DDD; padding: 6px 13px; background-color: #F8F8F8;', 'td': 'border: 1px solid #DDD; padding: 6px 13px;', 'th': 'border: 1px solid #DDD; padding: 6px 13px;', 'blockquote': 'border-left: .5ex solid #BFBFBF; margin-left: 0px; padding-left: 1em; margin-top: 1.4285em; margin-bottom: 1.4285em;', 'footnotes': 'border-top: 1px solid #9AB39B; font-size: 80%;', 'pre': 'color: #000000; font-family: monospace,monospace; font-size: 0.9em; white-space: pre-wrap; word-wrap: break-word; border: 1px solid #cccccc; border-radius: 3px; overflow: auto; padding: 6px 10px; margin-bottom: 10px;', 'hr': 'color:#9AB39B;background-color:#9AB39B;height:1px;border:none;', 'h1': 'margin-bottom: 1em; margin-top: 1.2em;', 'inline-code': 'color: #000000; font-family: monospace,monospace; padding: 0.1em 0.2em; margin: 0.1em; font-size: 85%; background-color: #F5F5F5; border-radius: 3px; border: 1px solid #cccccc;', 'tr:odd': 'border: 1px solid #DDD; padding: 6px 13px;', 'code': 'color: black; font-family: monospace,monospace; font-size: 0.9em;', 'sup': 'color:#6D6D6D;font-size:1ex;', 'table': 'border-collapse: collapse; border-spacing: 0; margin: 1em;', 'body': ''}, 
            'code-friendly': None, 
            'markdown-in-html': None, 
            'footnotes': None, 
            'metadata': None
        }
        MD_EXTRAS['fenced-code-blocks']['style'] = GithubStyle

        return MD_EXTRAS

    def extractTags(self, tags):
        try:
            tags = json.loads(tags)
        except:
            tags = [t.strip(' \t') for t in tags and tags.split(",") or []]
        return tags

    # 将内容转换成enml格式
    def getContent(self, body):
        content = '<?xml version="1.0" encoding="UTF-8"?>'
        content += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
        content += '<en-note%s>' % self.style
        content += body
        content += '</en-note>'
        return content
    
    # 获取笔记id
    def getNoteGuid(self, meta):
        nguid = None
        title = meta.get("title")
        intitle = 'intitle:' + '"' + title + '"'
        filter_data = NoteFilter(words=intitle, ascending=True)
        result = NotesMetadataResultSpec(includeTitle=True, includeNotebookGuid=True, includeTagGuids=True)
        re = self.noteStore.findNotesMetadata(self.dev_token, filter_data, 0, 500, result)
        resul = re.notes
        arrayLength = len(re.notes)
        for i in range(0, arrayLength):
            if resul[i].title == title:
                nguid = resul[i].guid
        return nguid

    # 创建笔记
    def createNote(self, meta, body):
        note = Types.Note()
        note.title = meta.get("title", note.title)
        tags = meta.get("tags", note.tagNames)
        if tags is not None:
            tags = self.extractTags(tags)
        note.tagNames = tags
        note.content = self.getContent(body)
        if "notebook" in meta:
            notebooks = self.noteStore.listNotebooks()
            for nb in notebooks:
                if nb.name == meta["notebook"]:
                    note.notebookGuid = nb.guid
                    break
        return note

    # 发送笔记
    def sendNote(self, note, isUpdate):
        try:
            if isUpdate:
                cnote = self.noteStore.updateNote(self.dev_token, note)
                print("Update note: %s" % note.title)
            else:
                cnote = self.noteStore.createNote(self.dev_token, note)
                print("Create note: %s" % note.title)
        except EDAMUserException as e:
            print('Evernote error:\n%s' % explain_error(e))
        except EDAMSystemException as e:
            print('Evernote error:\n%s' % explain_error(e))
        except Exception as e:
            print('Evernote plugin error %s' % e)

    # 批量推送笔记到evernote
    def batchPushToEver(self):
        if len(self.notes) == 0:
            print("无需更新")
            return

        for (path, title) in self.notes:
            infile = open(path,'r')
            contents = infile.read()
            infile.close()
            self.pushToEver(contents)

        self.setUploadtime()

    # 推送笔记到evernote
    def pushToEver(self, contents):
        body = markdown2.markdown(contents, extras=self.extras)
        
        if len(body.metadata.items()) > 0:
            meta = body.metadata
            note = self.createNote(meta, body)
            nguid = self.getNoteGuid(meta)
            note.guid = nguid
            self.sendNote(note, nguid is not None)
        else:
            print('Note format error! Loss matedata')

    # 获取目录中的所有文件
    def traversePath(self, root_path):
        ignoreList = ['.git', '.DS_Store', 'README.md']
        for filename in os.listdir(root_path):
            if filename in ignoreList:
                continue
            path = os.path.join(root_path, filename)
            if (os.path.isfile(path)):
                if path.endswith('.md'):
                    # 获取文件修改时间
                    mtime = os.stat(path).st_mtime
                    # 如果文件修改时间超过上次上传笔记时间
                    if mtime > self.lastUploadTime:
                        self.notes.append((path, filename))
            else:
                self.traversePath(path)


if __name__ == '__main__':
    if not sys.version_info.major == 3 and sys.version_info.minor >= 5:
        print("This script requires Python 3.5 or higher!")
        print("You are using Python {}.{}.".format(sys.version_info.major, sys.version_info.minor))
        sys.exit(1)

    #获取token https://app.yinxiang.com/api/DeveloperToken.action

    root_path = "/Users/nxmbp/Documents/Nutstore/Notes/"
    token = "S=s61:U=bc922e:E=186c08cc172:C=1869c803b98:P=1cd:A=en-devtoken:V=2:H=b3a312c5e198f7925f6de267740b08d2"
    manager = EverNoteManager(token, False)
    manager.traversePath(root_path)
    manager.batchPushToEver()
