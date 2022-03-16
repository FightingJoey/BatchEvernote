# -*- coding: utf-8 

from evernote.api.client import EvernoteClient
import evernote.edam.type.ttypes as Types
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from pygmstyles import markdown2
import os
import json

def getExtras():
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

    wrapper_style = ''
    if 'inline-css' in MD_EXTRAS:
        wrapper_style = MD_EXTRAS['inline-css'].get('body', "")
        if len(wrapper_style) > 0:
            wrapper_style = ' style="%s"' % wrapper_style
    return MD_EXTRAS, wrapper_style

def getContent(body, wrapper_style):
    content = '<?xml version="1.0" encoding="UTF-8"?>'
    content += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
    content += '<en-note%s>' % wrapper_style
    content += body
    content += '</en-note>'
    return content

def extractTags(tags):
    try:
        tags = json.loads(tags)
    except:
        tags = [t.strip(' \t') for t in tags and tags.split(",") or []]
    return tags

# if (nguid) {
#     vscode.window.setStatusBarMessage("Updating to server.", 2000);
#     const updateNote = await updateNoteOnServer(meta, content, resources, nguid);
#     updateNote.resources = resources;
#     if (!notesMap[updateNote.notebookGuid]) {
#       notesMap[updateNote.notebookGuid] = [updateNote];
#     } else {
#       notesMap[updateNote.notebookGuid].push(updateNote);
#     }
#     localNote[doc.fileName] = updateNote;
#     let notebookName = notebooks.find(notebook => notebook.guid === updateNote.notebookGuid).name;
#     attachmentsCache[doc.fileName] = [];
#     return vscode.window.showInformationMessage(`${notebookName}>>${title} update to server successfully.`);
#   } else {
#     vscode.window.setStatusBarMessage("Creating the note.", 2000);
#     const createdNote = await createNote(meta, content, resources);
#     createdNote.resources = resources;
#     if (!notesMap[createdNote.notebookGuid]) {
#       notesMap[createdNote.notebookGuid] = [createdNote];
#     } else {
#       notesMap[createdNote.notebookGuid].push(createdNote);
#     }
#     localNote[doc.fileName] = createdNote;
#     let notebookName = notebooks.find(notebook => notebook.guid === createdNote.notebookGuid).name;
#     attachmentsCache[doc.fileName] = [];
#     return vscode.window.showInformationMessage(`${notebookName}>>${title} created successfully.`);
#   }

def getNoteGuid(meta, client, noteStore):
    title = meta.get("title")
    intitle = 'intitle:' + '"' + title + '"'
    re = client.listMyNotes(intitle)
    filter = NoteFilter(words=intitle, ascending=True)
    noteStore.findNotesMetadata(authenticationToken='')
    resul = re.notes
    arrayLength = resul.length
    pass

if __name__ == '__main__':
    infile = open('/Users/kaola/Nutstore Files/Notes/00@未分类/洛克菲勒写给儿子的38封信 - 读书笔记.md','r')
    contents = infile.read()
    infile.close()

    MD_EXTRAS, wrapper_style = getExtras()
    body = markdown2.markdown(contents, extras=MD_EXTRAS)

    meta = body.metadata or {}

    dev_token = "S=s61:U=bc922e:E=17fb42a1455:C=17f901d8c90:P=1cd:A=en-devtoken:V=2:H=a965be21f77c3c01c44880df4500d9b3"
    client = EvernoteClient(token=dev_token, sandbox=False, china=True)
    userStore = client.get_user_store()
    user = userStore.getUser()

    # print(user)

    noteStore = client.get_note_store()

    nguid = None
    title = meta.get("title")
    intitle = 'intitle:' + '"' + title + '"'
    # re = client.listMyNotes(intitle)
    filter = NoteFilter(words=intitle, ascending=True)
    result = NotesMetadataResultSpec(includeTitle=True, includeNotebookGuid=True, includeTagGuids=True)
    re = noteStore.findNotesMetadata(dev_token, filter, 0, 500, result)
    resul = re.notes
    arrayLength = len(re.notes)
    for i in range(0, arrayLength):
        if resul[i].title == title:
            nguid = resul[i].guid

    note = Types.Note()
    note.title = meta.get("title", note.title)
    tags = meta.get("tags", note.tagNames)
    if tags is not None:
        tags = extractTags(tags)
    note.tagNames = tags
    note.content = getContent(body, wrapper_style)
    if "notebook" in meta:
        notebooks = noteStore.listNotebooks()
        for nb in notebooks:
            if nb.name == meta["notebook"]:
                note.notebookGuid = nb.guid
                break

    note = noteStore.createNote(note)

    

