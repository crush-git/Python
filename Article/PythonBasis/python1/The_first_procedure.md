# 三、第一个 Python 程序 #

好了，说了那么多，现在我们可以来写一下第一个 Python 程序了。

一开始写 Python 程序，个人不太建议用专门的工具来写，不方便熟悉语法，所以这里我先用 [Sublime Text](http://www.sublimetext.com/) 来写，后期可以改为用 PyCharm 。

第一个 Python 程序当然是打印 Hello Python 啦。

如果你没编程经验，什么都不懂，没关系，第一个 Python 程序，只要跟着做，留下个印象，尝试一下就好。

新建一个文件，命名为 `HelloPython.py` , 注意，这里是以 `.py` 为后缀的文件。

然后打开文件，输入 `print('Hello Python')`


```python
print('Hello Python')
```


最后就可以打开命令行窗口，把当前目录切换到 HelloPython.py 所在目录，就可以运行这个程序了，下面就是运行的结果。


```
C:\Users\Administrator>cd C:\Users\Administrator\Desktop\Python

C:\Users\Administrator\Desktop\Python>python HelloPython.py
Hello Python

C:\Users\Administrator\Desktop\Python>
```


当然，如果你是使用  [Sublime Text](http://www.sublimetext.com/) ，并且在安装 Python 的时候配置好了环境变量，直接按 Ctrl + B 就可以运行了，运行结果如下：

这里要注意，记得在 Sublime Text 右下角的语法选择那里，选择 `Python` ，否则按 Ctrl + B 是没法正确执行的。运行后在编辑器底部的输出窗口就能看到结果：

```
Hello Python
[Finished in 0.5s]
```

