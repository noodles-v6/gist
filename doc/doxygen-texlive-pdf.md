# 用 Doxygen 和 Texlive 快速生成代码文档

## Doxygen 

Doxygen 是开源的非常好用的代码文档生成工具，支持常见的C、C++、Java、idl、markdown等语言。

使用 Doxygen 生成的文档格式有 html、latex、rft。html 便于放到服务器上，latex 便于使用工业
排版技术生成专业文档，rft便于生存word。

## Texlive

Texlive 是最常用的工业排版工具，他能够把 .tex 格式的文档转换为pdf格式，非常的好用。

不过中文需要处理一下，首先系统要有中文字体，其次要私用CJK技术。如在文档中要加上，

    \usepackage{xeCJK}[2011/05/20]
    \setCJKmainfont{Adobe Fangsong Std}

## 更多

请访问 Doxygen Texlive CJK 主页
