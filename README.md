# BatchEvernote
作为开发者，平时喜欢使用markdown写一些文章，然后为了将笔记同步到印象笔记中，之前也采用了很多方案：

- Sublime Text 插件：[sublime-evernote](https://github.com/bordaigorl/sublime-evernote)
- VSCode 插件：[evermonkey](https://github.com/michalyao/evermonkey)
- MWeb：[官方网站](https://zh.mweb.im/)

但是他们都有一些局限性，一次只能上传一篇文章，而我有时候会写很多篇，这样同步的时候就会很麻烦，就导致我很多时候懒得去同步。结果在经历了一次电脑意外进水，硬盘内容全部丢失之后，我决定还是自己写一个，可以批量将markdown笔记同步到印象笔记的python脚本。

在编写的时候，很大一部分内容参考了 sublime-evernote 插件和印象笔记开发者文档。

> 目前这个脚本还只适合开发者使用，因为它需要python3环境和一些python库，后续可能会开发一个专门的Mac APP 来做这件事，但是估计要等一段时间了~

### Developer Token

我们可以访问网页版印象笔记，登录后，访问 [印象笔记 Developer Token](https://app.yinxiang.com/api/DeveloperToken.action)，然后点击其中的 `Create a developer token`。就会生成一个 Developer Token 和 NoteStore URL，我们需要把这个 token 保存下来。

> 这个 token 的有效期现在只有一周，所以也挺麻烦的。

使用的时候，打开 evernote.py，用刚才获取到的 token 替换 `__main__` 函数中的 token，然后运行。

### OAuth

基于OAuth的认证流程就是，用户在自己的设备上通过印象笔记账户认证你的应用程序的过程。用户必须通过印象笔记域名下的网站认证你的应用的访问权限(*app.yinxiang.com* 或者 *sandbox.yinxiang.com*)。在认证被授权（或是被拒绝）之后，印象笔记将会把用户重定向回你的应用程序，同时你会收到一些必要的信息，来取回一个access token。这个access token使你可以在用户的设备上使用这个用户的印象笔记的数据。

由于我们的只是个脚本，暂时没办法使用这种方式。
