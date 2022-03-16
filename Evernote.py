# -*- coding: utf-8 

from evernote.api.client import EvernoteClient
import evernote.edam.type.ttypes as Types
from pygmstyles import markdown2
import os

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


if __name__ == '__main__':
    infile = open('/Users/kaola/Nutstore Files/Notes/00@未分类/洛克菲勒写给儿子的38封信 - 读书笔记.md','r')
    contents = infile.read()
    infile.close()

    MD_EXTRAS, wrapper_style = getExtras()
    body = markdown2.markdown(contents, extras=MD_EXTRAS)

    dev_token = "S=s61:U=bc922e:E=17fb42a1455:C=17f901d8c90:P=1cd:A=en-devtoken:V=2:H=a965be21f77c3c01c44880df4500d9b3"
    client = EvernoteClient(token=dev_token, sandbox=False, china=True)
    userStore = client.get_user_store()
    user = userStore.getUser()

    # print(user)

    noteStore = client.get_note_store()
    # notebooks = noteStore.listNotebooks()
    # for n in notebooks:
    #     print(n.name)

    for i in range(2):
        note = Types.Note()
        note.title = "I'm a test note! %d" % i
        note.content = getContent(body, wrapper_style)
        note = noteStore.createNote(note)

    

