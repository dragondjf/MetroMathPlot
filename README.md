MetroMathPlot is an application based on PyQt4 with Metro style
========================================================
####关于
>MetroMathPlot 是基于PyQt4开发，采用Metro风格的应用程序。  

### 如何执行
> 在cmd中执行ython MetroMathPlot.py即可

### 环境搭建
 python2.7 + PyQt4 + matplotlib
>
>#### windows下环境搭建
>>##### PyQt4安装
>> pip isntall python-qt
>####matplotlib 安装
>> pip install matplotlib  
>
>#### linux下环境搭建
>>##### PyQt4安装
>> sudo pip install python-qt
>####matplotlib 安装
>> pip install matplotlib  
>>>matlplotlib安装注意：
>>>> <blod>1.<blod> gcc: error trying to exec ‘cc1plus’: execvp: No such file or directory
>>>>>解决方法：sudo apt-get install build-essential

>>>><blod>2.<blod> src/ft2font.h:13:22: fatal error: ft2build.h: No such file or directory
>>>>>解决方法：sudo apt-get install  libfreetype6-dev

>>>><blod>3.<blod> src/backend_agg.cpp:3:17: fatal error: png.h: No such file or directory
>>>>>解决方法：sudo apt-get install libpng-dev  

>>##### guiqwt安装
>>cd guiqwt   
>>python setup.py build_ext --fcompiler=gnu95 build install
>> 参考<a>http://pythonhosted.org/guiqwt/installation.html#id1</a>  
>>>注意：guiqwt依赖pyqwt，但linux的python-qt库中没有绑定这个库，需要额外安装，所以在装guiqwt后还需要进行如下操作:  
>>>sudo apt-get install  python-qwt5-qt4




