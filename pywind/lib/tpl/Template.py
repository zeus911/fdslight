#!/usr/bin/env python3

import pywind.lib.tpl.syntax_execute as core_execute
import os, importlib


class TemplateErr(Exception): pass


class template(object):
    __user_exts = None
    __kwargs = None
    __directories = None

    # 执行对象,一个模版文件代表一个执行对象
    __exe_objects = None

    __render_content = None

    def __ext_inherit(self, uri):
        """实现继承功能
        :param uri: 
        :return: 
        """
        fpath = self.__get_fpath(uri)
        if not fpath: raise TemplateErr("cannot found inherit template '%s'" % uri)

        fdst = open(fpath, "r")
        text_content = fdst.read()
        fdst.close()

        exeobj = core_execute.execute(**self.__kwargs)
        self.__register_exts(exeobj)

        # 首先生成语法树
        exeobj._gen_syntax_tree(text_content)
        self.__exe_objects.append(exeobj)

    def __ext_dyn_include(self, uri):
        """在执行期间动态包含文件
        :param uri: 
        :return: 
        """
        content = self.__include(uri)

        return self.render_string(content, **self.__kwargs)

    def __init__(self, user_exts={}):
        """
        :param user_exts:添加的自定义扩展 
        :param kwargs: 
        """
        self.__user_exts = user_exts
        self.__directories = []
        self.__exe_objects = []
        self.__render_content = []

    def set_find_directories(self, directories):
        """设置查找目录
        :param directories: 
        :return: 
        """
        if not isinstance(directories, list) and not isinstance(directories, tuple):
            raise ValueError("the directories must be tuple or list")
        self.__directories = directories

    def __include(self, uri):
        fpath = self.__get_fpath(uri)
        if not fpath: raise TemplateErr("cannot found include file '%s'" % uri)

        with open(fpath, "r") as f:
            content = f.read()
        f.close()

        return content

    def __register_exts(self, exeobj):
        """注册扩展
        :return: 
        """

        for k, v in self.__user_exts:
            exeobj.register_ext_attr(k, v)

        exeobj.register_ext_attr("inherit", self.__ext_inherit)
        exeobj._set_include_func(self.__include)
        exeobj.register_ext_attr("include", self.__ext_dyn_include)
        exeobj.register_ext_attr("time", importlib.import_module("time"))

    def __get_fpath(self, uri):
        for d in self.__directories:
            fpath = "%s/%s" % (d, uri,)
            if os.path.isfile(fpath):
                return fpath
            ''''''
        return None

    def render(self, uri, **kwargs):

        fpath = self.__get_fpath(uri)
        if not fpath: raise TemplateErr("cannot found template file '%s'" % uri)

        fdst = open(fpath, "r")
        text_content = fdst.read()

        fdst.close()

        return self.render_string(text_content, **kwargs)

    def render_string(self, s, **kwargs):
        self.__kwargs = kwargs

        exeobj = core_execute.execute(**kwargs)

        self.__register_exts(exeobj)

        exeobj._gen_syntax_tree(s)
        exeobj_a = exeobj

        while 1:
            try:
                exeobj_b = self.__exe_objects.pop(0)
            except IndexError:
                break

            for k, v in exeobj_a.block_map.items():
                exeobj_b.block_map[k] = v

            exeobj_a = exeobj_b

        exeobj_a._exe()

        return exeobj_a._get_buff_content()


tpl = template()
tpl.set_find_directories(["./test"])
rs = tpl.render("child.html", name="this is template")

print(rs)