# -*- coding: utf-8 -*-

# region 导入依赖包
import os
import sys
import shutil
from os.path import isdir, isfile
from pathlib import Path

模块名 = 'DebugInfo'
try:
    from DebugInfo.DebugInfo import *
except ImportError as impErr:
    print(f"尝试导入 {模块名} 依赖时检测到异常：{impErr}")
    print(f"尝试安装 {模块名} 模块：")
    try:
        os.system(f"pip install {模块名}")
    except OSError as osErr:
        print(f"尝试安装模块 {模块名} 时检测到异常：{osErr}")
        exit(0)
    else:
        try:
            from DebugInfo.DebugInfo import *
        except ImportError as impErr:
            print(f"再次尝试导入 {模块名} 依赖时检测到异常：{impErr}")
            exit(0)

路径分隔符: str = '\\' if 在nt系统中() else '/'

# ⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊
# 本脚本依赖于 getGitVer.py 脚本提供的函数功能来获取 git 仓库的版本信息，所以您需要在此指定 getGitVer.py 的位置
sys.path.append(os.path.expanduser('~') + 路径分隔符 + "gitVersion")  # ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

try:
    import gitVerInfo
except ImportError as impErr:
    gitVerInfo = None
    print("尝试导入 gitVerInfo 依赖时检测到异常：", impErr)
    exit(0)
# endregion

# 定义一个 commandArgs 类，用于记录和传递命令行参数
class 命令行参数类(入参基类):
    def __init__(self):
        # 初始化基类
        super().__init__()

        # region 添加命令行参数
        self._添加参数('publishType_0Private_1Public_2Both', int, '指定版本的类型', 1)  # 默认 publishType 为 1：for public
        self._添加参数('outputType_0PublishObj_1PrintGitVer', int, '请指定是发布文档,或者是打印版本历史', 0)  # 默认 outputType 为 0： for publishObj
        self._添加参数('productID', str, '指定产品ID')
        self._添加参数('objsToBePublished',str,'指定要发布的文档，或者文件夹，可以带路径，多个文档使用"，"分隔')
        self._添加参数('tgtDirForPublishing',str,'指定发布的目标位置，可以是相对路径或者全路径')
        self._添加参数('gitRePoDir', str, '用于解析 git 版本信息的 git 仓库路径')
        self._添加参数('majorBranchName', str, '用于追踪major版本的分支名称')
        self._添加参数('tagPrefix_major', str, 'major分支上被追踪版本信息的tag的前缀')
        self._添加参数('minorBranchName', str, '用于追踪minor版本的分支名称')
        self._添加参数('tagPrefix_minor', str, 'minor分支上被追踪版本信息的tag的前缀')
        self._添加参数('anchorChar', str, '打印版本记录时，用于标记版本节点的符号')
        self._添加参数('focusDoc_fileName', str, '用于 需要特别标记的兴趣文档的文档名')
        self._添加参数('gitVerSql_host', str, '用于存储管理 gitVer 信息的数据库 host 信息')
        self._添加参数('gitVerSql_user', str, '用于存储管理 gitVer 信息的数据库 user 信息')
        self._添加参数('gitVerSql_pwd', str, '用于存储管理 gitVer 信息的数据库 password 信息')
        self._添加参数('gitVerSql_db', str, '用于存储管理 gitVer 信息的数据库 database 信息')
        self._添加参数('gitVerSql_charset', str, '用于存储管理 gitVer 信息的数据库 charset 信息')
        self._添加参数('gitVerSql_table', str, '用于存储管理 gitVer 信息的数据库 tableName 信息')
        self._添加参数('showLogs', None, '如果你需要打印log，请使用该参数')
        self._添加参数('showTags', None, '如果你需要打印展示所有的tag，请使用该参数')
        self._添加参数('logsCount', int, '如果你需要打印log，您希望显示的log的数量', 5)
        self._添加参数('AllBranches', None, '如果你需要打印所有分支的log，请使用该参数; 否则只打印当前分支的log')
        self._添加参数('copy', None, '如果需要将版本复制入粘贴板，请使用该参数')
        # endregion

        # 定义个性化成员
        # 定义一gitVerInfoCfg 对象，用于保存对应的配置信息,并设置默认值
        self.gitVerInfoCfg: gitVerInfo.GitVerInfoCfg = gitVerInfo.GitVerInfoCfg(gitRePoDir=os.getcwd(),
                                                                                majorBranchName='master',
                                                                                tagPrefix_major='m',
                                                                                minorBranchName='release',
                                                                                tagPrefix_minor='r',
                                                                                anchorChar='⚓')

    # region 访问器
    @property
    def jsonCfg(self) -> str:
        if 'jsonCfg' in self._参数字典:
            return self._参数字典['jsonCfg'].值
        else:
            return ''

    @jsonCfg.setter
    def jsonCfg(self, 值: str):
        if 'jsonCfg' in self._参数字典:
            self._参数字典['jsonCfg'].值 = str(值)

    @property
    def publishType_0Private_1Public_2Both(self) -> int:
        if 'publishType_0Private_1Public_2Both' in self._参数字典:
            return self._参数字典['publishType_0Private_1Public_2Both'].值
        else:
            return 0

    @publishType_0Private_1Public_2Both.setter
    def publishType_0Private_1Public_2Both(self, 值: int):
        if 'publishType_0Private_1Public_2Both' in self._参数字典:
            if type(值) in [int, float]:
                self._参数字典['publishType_0Private_1Public_2Both'].值 = int(值)

    @property
    def outputType_0PublishObj_1PrintGitVer(self) -> int:
        if 'outputType_0PublishObj_1PrintGitVer' in self._参数字典:
            return self._参数字典['outputType_0PublishObj_1PrintGitVer'].值
        else:
            return 0

    @outputType_0PublishObj_1PrintGitVer.setter
    def outputType_0PublishObj_1PrintGitVer(self, 值: int):
        if 'outputType_0PublishObj_1PrintGitVer' in self._参数字典:
            if type(值) in [int, float]:
                self._参数字典['outputType_0PublishObj_1PrintGitVer'].值 = int(值)

    @property
    def productID(self) -> str:
        if 'productID' in self._参数字典:
            return self._参数字典['productID'].值
        else:
            return ''

    @productID.setter
    def productID(self, 值: str):
        if 'productID' in self._参数字典:
            self._参数字典['productID'].值 = str(值)

    @property
    def projectName(self) -> str:
        if 'projectName' in self._参数字典:
            return self._参数字典['projectName'].值
        else:
            return ''

    @projectName.setter
    def projectName(self, 值: str):
        if 'projectName' in self._参数字典:
            self._参数字典['projectName'].值 = str(值)

    @property
    def objsToBePublished(self) -> str:
        if 'objsToBePublished' in self._参数字典:
            return self._参数字典['objsToBePublished'].值
        else:
            return ''

    @objsToBePublished.setter
    def objsToBePublished(self, 值: str):
        if 'objsToBePublished' in self._参数字典:
            self._参数字典['objsToBePublished'].值 = str(值)

    @property
    def tgtDirForPublishing(self) -> str:
        if 'tgtDirForPublishing' in self._参数字典:
            return self._参数字典['tgtDirForPublishing'].值
        else:
            return ''

    @tgtDirForPublishing.setter
    def tgtDirForPublishing(self, 值: str):
        if 'tgtDirForPublishing' in self._参数字典:
            self._参数字典['tgtDirForPublishing'].值 = str(值)

    @property
    def gitRePoDir(self) -> str:
        if 'gitRePoDir' in self._参数字典:
            return self._参数字典['gitRePoDir'].值
        else:
            return ''

    @gitRePoDir.setter
    def gitRePoDir(self, 值: str):
        if 'gitRePoDir' in self._参数字典:
            self._参数字典['gitRePoDir'].值 = str(值)

    @property
    def majorBranchName(self) -> str:
        if 'majorBranchName' in self._参数字典:
            return self._参数字典['majorBranchName'].值
        else:
            return ''

    @majorBranchName.setter
    def majorBranchName(self, 值: str):
        if 'majorBranchName' in self._参数字典:
            self._参数字典['majorBranchName'].值 = str(值)

    @property
    def tagPrefix_major(self) -> str:
        if 'tagPrefix_major' in self._参数字典:
            return self._参数字典['tagPrefix_major'].值
        else:
            return ''

    @tagPrefix_major.setter
    def tagPrefix_major(self, 值: str):
        if 'tagPrefix_major' in self._参数字典:
            self._参数字典['tagPrefix_major'].值 = str(值)

    @property
    def minorBranchName(self) -> str:
        if 'minorBranchName' in self._参数字典:
            return self._参数字典['minorBranchName'].值
        else:
            return ''

    @minorBranchName.setter
    def minorBranchName(self, 值: str):
        if 'minorBranchName' in self._参数字典:
            self._参数字典['minorBranchName'].值 = str(值)

    @property
    def tagPrefix_minor(self) -> str:
        if 'tagPrefix_minor' in self._参数字典:
            return self._参数字典['tagPrefix_minor'].值
        else:
            return ''

    @tagPrefix_minor.setter
    def tagPrefix_minor(self, 值: str):
        if 'tagPrefix_minor' in self._参数字典:
            self._参数字典['tagPrefix_minor'].值 = str(值)

    @property
    def anchorChar(self) -> str:
        if 'anchorChar' in self._参数字典:
            return self._参数字典['anchorChar'].值
        else:
            return ''

    @anchorChar.setter
    def anchorChar(self, 值: str):
        if 'anchorChar' in self._参数字典:
            self._参数字典['anchorChar'].值 = str(值)

    @property
    def focusDoc_fileName(self) -> str:
        if 'focusDoc_fileName' in self._参数字典:
            return self._参数字典['focusDoc_fileName'].值
        else:
            return ''

    @focusDoc_fileName.setter
    def focusDoc_fileName(self, 值: str):
        if 'focusDoc_fileName' in self._参数字典:
            self._参数字典['focusDoc_fileName'].值 = str(值)

    @property
    def gitVerSql_host(self) -> str:
        if 'gitVerSql_host' in self._参数字典:
            return self._参数字典['gitVerSql_host'].值
        else:
            return ''

    @gitVerSql_host.setter
    def gitVerSql_host(self, 值: str):
        if 'gitVerSql_host' in self._参数字典:
            self._参数字典['gitVerSql_host'].值 = str(值)

    @property
    def gitVerSql_user(self) -> str:
        if 'gitVerSql_user' in self._参数字典:
            return self._参数字典['gitVerSql_user'].值
        else:
            return ''

    @gitVerSql_user.setter
    def gitVerSql_user(self, 值: str):
        if 'gitVerSql_user' in self._参数字典:
            self._参数字典['gitVerSql_user'].值 = str(值)

    @property
    def gitVerSql_pwd(self) -> str:
        if 'gitVerSql_pwd' in self._参数字典:
            return self._参数字典['gitVerSql_pwd'].值
        else:
            return ''

    @gitVerSql_pwd.setter
    def gitVerSql_pwd(self, 值: str):
        if 'gitVerSql_pwd' in self._参数字典:
            self._参数字典['gitVerSql_pwd'].值 = str(值)

    @property
    def gitVerSql_db(self) -> str:
        if 'gitVerSql_db' in self._参数字典:
            return self._参数字典['gitVerSql_db'].值
        else:
            return ''

    @gitVerSql_db.setter
    def gitVerSql_db(self, 值: str):
        if 'gitVerSql_db' in self._参数字典:
            self._参数字典['gitVerSql_db'].值 = str(值)

    @property
    def gitVerSql_charset(self) -> str:
        if 'gitVerSql_charset' in self._参数字典:
            return self._参数字典['gitVerSql_charset'].值
        else:
            return ''

    @gitVerSql_charset.setter
    def gitVerSql_charset(self, 值: str):
        if 'gitVerSql_charset' in self._参数字典:
            self._参数字典['gitVerSql_charset'].值 = str(值)

    @property
    def gitVerSql_table(self) -> str:
        if 'gitVerSql_table' in self._参数字典:
            return self._参数字典['gitVerSql_table'].值
        else:
            return ''

    @gitVerSql_table.setter
    def gitVerSql_table(self, 值: str):
        if 'gitVerSql_table' in self._参数字典:
            self._参数字典['gitVerSql_table'].值 = str(值)

    @property
    def showLogs(self) -> bool or None:
        if 'showLogs' in self._参数字典:
            return self._参数字典['showLogs'].值
        else:
            return None

    @showLogs.setter
    def showLogs(self, 值: bool):
        if 'showLogs' in self._参数字典:
            if isinstance(值, bool):
                self._参数字典['showLogs'].值 = 值
            else:
                self._参数字典['showLogs'].值 = None

    @property
    def showTags(self) -> bool or None:
        if 'showTags' in self._参数字典:
            return self._参数字典['showTags'].值
        else:
            return None

    @showTags.setter
    def showTags(self, 值: bool):
        if 'showTags' in self._参数字典:
            if isinstance(值, bool):
                self._参数字典['showTags'].值 = 值
            else:
                self._参数字典['showTags'].值 = None

    @property
    def logsCount(self) -> int:
        if 'logsCount' in self._参数字典:
            return self._参数字典['logsCount'].值
        else:
            return 0

    @logsCount.setter
    def logsCount(self, 值: int):
        if 'logsCount' in self._参数字典:
            if type(值) in [int, float]:
                self._参数字典['logsCount'].值 = int(值)

    @property
    def AllBranches(self) -> bool or None:
        if 'AllBranches' in self._参数字典:
            return self._参数字典['AllBranches'].值
        else:
            return None

    @AllBranches.setter
    def AllBranches(self, 值: bool):
        if 'AllBranches' in self._参数字典:
            if isinstance(值, bool):
                self._参数字典['AllBranches'].值 = 值
            else:
                self._参数字典['AllBranches'].值 = None

    @property
    def copy(self) -> bool or None:
        if 'copy' in self._参数字典:
            return self._参数字典['copy'].值
        else:
            return None

    @copy.setter
    def copy(self, 值: bool):
        if 'copy' in self._参数字典:
            if isinstance(值, bool):
                self._参数字典['copy'].值 = 值
            else:
                self._参数字典['copy'].值 = None

    # endregion

    def 读取Json配置(self, 画板: 打印模板 = None):
        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
        画板.执行位置(self.__class__, self.读取Json配置)

        # 如果存在配置文件，则读取配置文件内的配置
        gitVerInfoCfg = 'gitVerInfoCfg.json'
        if os.path.exists(gitVerInfoCfg):
            super().解析Json(jsonCfg=gitVerInfoCfg , 画板=画板.副本)
            self.gitVerInfoCfg.readJson(gitVerInfoCfgDir=os.path.abspath(gitVerInfoCfg),
                                        白板=画板.副本.缩进())

    # 重新定义方法 解析入参
    def 解析入参(self, 画板: 打印模板 = None):
        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
        画板.执行位置(self.__class__, self.解析入参)

        # 如果存在配置文件，则读取配置文件内的配置
        self.读取Json配置(画板=画板.副本.缩进())

        # 解析命令行参数
        super().解析入参(画板=画板.副本.缩进())

        # 使用命令行参数调整默认参数
        if self.gitRePoDir:
            self.gitVerInfoCfg.gitRePoDir = self.gitRePoDir
        if self.majorBranchName:
            self.gitVerInfoCfg.majorBranchName = self.majorBranchName
        if self.tagPrefix_major:
            self.gitVerInfoCfg.tagPrefix_major = self.tagPrefix_major
        if self.minorBranchName:
            self.gitVerInfoCfg.minorBranchName = self.minorBranchName
        if self.tagPrefix_minor:
            self.gitVerInfoCfg.tagPrefix_minor = self.tagPrefix_minor
        if self.anchorChar:
            self.gitVerInfoCfg.anchorChar = self.anchorChar
        if self.focusDoc_fileName:
            self.gitVerInfoCfg.focusDoc_fileName = self.focusDoc_fileName

    # 重新定义方法 展示
    def 展示(self, 画板: 打印模板 = None):
        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
        画板.执行位置(self.__class__, self.展示)

        画板.消息('ARGS:', 蓝字(self._ARGS))

        画板.准备表格()
        画板.添加一行('publishType_0Private_1Public_2Both:', self.publishType_0Private_1Public_2Both)
        画板.添加一行('outputType_0PublishObj_1PrintGitVer:', self.outputType_0PublishObj_1PrintGitVer)
        画板.添加一行('objsToBePublished:', 黄字(self.objsToBePublished))
        画板.添加一行('tgtDirForPublishing:',self.tgtDirForPublishing)
        画板.添加一行('showLogs:', self.showLogs)
        画板.添加一行('logsCount:', self.logsCount)
        if 画板.调试状态:
            画板.添加一行('debug model:', 红字(画板.调试状态))
        else:
            画板.添加一行('debug model:', 绿字(画板.调试状态))
        画板.展示表格()

        # 展示 gitVerInfoCfg 信息
        self.gitVerInfoCfg.showInfo(白板=画板.副本.缩进())


def 发布产品(userArgs: 命令行参数类 = None,
             日期语义化:bool = False,
             画板: 打印模板 = None) -> bool:
    画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
    画板.执行位置(__file__, 发布产品)

    # region 检查入参
    userArgs = userArgs if isinstance(userArgs, 命令行参数类) else 命令行参数类()
    日期语义化 = True if 日期语义化 else False
    # endregion

    if not userArgs.gitRePoDir or not isdir(userArgs.gitRePoDir):
        画板.提示错误('仓库地址无效', ':' + userArgs.gitRePoDir if userArgs.gitRePoDir else '')
        return False

    if not userArgs.gitVerInfoCfg.projectName:
        画板.提示错误('projectName is invalid')
        return False

    if not userArgs.outputType_0PublishObj_1PrintGitVer == 0:
        画板.提示错误('outputType is noMatched:', userArgs.outputType_0PublishObj_1PrintGitVer)

    if not userArgs.objsToBePublished:
        画板.提示错误('objs will be published is inValid')
        return False

    if not userArgs.tgtDirForPublishing or not isdir(userArgs.tgtDirForPublishing):
        画板.提示错误('tgtDirForPublishing is invalid', ':' + userArgs.tgtDirForPublishing if userArgs.tgtDirForPublishing else '')
        return False
    userArgs.tgtDirForPublishing = userArgs.tgtDirForPublishing.strip().replace('\\', '/').rstrip('/')

    目标列表: list[str]
    方式列表: list[str] = []
    目标列表 = userArgs.objsToBePublished.strip().replace(',','|').replace('，', '|').replace('｜', '|').split('|')
    if not 目标列表:
        画板.提示错误('objs will be publish is inValid:', userArgs.objsToBePublished)
    else:
        目标列表 = [目标.strip() for 目标 in 目标列表]
        for idx in range(len(目标列表)):
            目标 = 目标列表[idx].replace('@', '@')
            if '@' not in 目标:
                目标列表[idx] = 目标
                方式列表.append('move')
            else:
                项, 方式 = 目标.split('@')
                目标列表[idx] = 项.strip()
                if 方式.lower() in ['copy', 'move']:
                    方式列表.append(方式.lower())
                else:
                    方式列表.append('move')

        画板.准备表格()
        画板.添加一行('序号','文档/文件夹','类型', '方式','检测结果').修饰行(黄字)
        画板.添加分隔行()
        无效目标数量: int = 0
        for idx in range(len(目标列表)):
            目标 = 目标列表[idx]
            方式 = 方式列表[idx]
            if 目标 and isfile(目标):
                画板.添加一行(画板.表格行数 - 1, 目标, '文档', 方式, 绿字('✔'))
            elif 目标 and isdir(目标):
                画板.添加一行(画板.表格行数 - 1, 目标, '文件夹', 方式, 绿字('✔'))
            else:
                画板.添加一行(画板.表格行数 - 1, 目标, '-', 方式, 红字('x'))
                无效目标数量 += 1

        if 画板.表格行数> 1:
            画板.展示表格()

    thisV: gitVerInfo.GitVerInfo = gitVerInfo.GitVerInfo(userArgs.gitVerInfoCfg)
    flg = thisV.versionDecode()
    if not flg:
        画板.提示错误('版本解析失败')
        return False

    gitV_private = thisV.repoInfo.verInfo.privateVersion
    gitV_public = thisV.repoInfo.verInfo.publicVersion

    # 文档名合规处理, 避免无效字符出现在文件夹名中
    gitV_private = (gitV_private.
                    replace('/','／').
                    replace('\\','＼').
                    replace(':','：').
                    replace('|','｜').
                    replace('<','〈').
                    replace('>','〉'))
    gitV_public = (gitV_public.
                    replace('/', '／').
                    replace('\\', '＼').
                    replace(':', '：').
                    replace('|', '｜').
                    replace('<', '〈').
                    replace('>', '〉'))
    tgtFolder_private: str = userArgs.tgtDirForPublishing + f'/{userArgs.gitVerInfoCfg.projectName}_{gitV_private}'
    tgtFolder_public: str = userArgs.tgtDirForPublishing + f'/{userArgs.gitVerInfoCfg.projectName}_{gitV_public}'

    if isdir(tgtFolder_private):
        画板.提示错误(f'发布目标路径已经存在: {tgtFolder_private}')
        return False
    if isdir(tgtFolder_public):
        画板.提示错误(f'发布目标路径已经存在: {tgtFolder_public}')
        return False
    try:
        if userArgs.publishType_0Private_1Public_2Both in [0, 2]:
            if not isdir(tgtFolder_private):
                Path(tgtFolder_private).mkdir(parents=True, exist_ok=True)
            if not isdir(tgtFolder_private):
                画板.提示错误(f'无法创建目标文件夹: {tgtFolder_private}')
                return False
            flg, _ = thisV.repoInfo.verInfo.saveTagsList(objPublished=tgtFolder_private,
                                                         saveType_0Private_1Public_2Both=userArgs.publishType_0Private_1Public_2Both,
                                                         语义化提交日期=False)
            if not flg:
                画板.提示错误('tagsList 创建失败')
                return False

            for idx in range(len(目标列表)):
                目标 = 目标列表[idx]
                方式 = 方式列表[idx]
                if isfile(目标):
                    if 方式 == 'copy':
                        shutil.copy2(目标, tgtFolder_private)
                    else:
                        shutil.move(目标, tgtFolder_private)
                if isdir(目标):
                    if 方式 == 'copy':
                        shutil.copytree(目标, os.path.join(tgtFolder_private, 目标))
                    else:
                        shutil.move(目标, os.path.join(tgtFolder_private, 目标))

            画板.消息(f'publishing done: {黄字(tgtFolder_private)} {绿字("✔")}')
        if userArgs.publishType_0Private_1Public_2Both in [1, 2]:
            if not isdir(tgtFolder_public):
                Path(tgtFolder_public).mkdir(parents=True, exist_ok=True)
            if not isdir(tgtFolder_private):
                画板.提示错误(f'无法创建目标文件夹: {tgtFolder_public}')
                return False
            flg, _ = thisV.repoInfo.verInfo.saveTagsList(objPublished=tgtFolder_public,
                                                         saveType_0Private_1Public_2Both=userArgs.publishType_0Private_1Public_2Both,
                                                         语义化提交日期=False)
            if not flg:
                画板.提示错误('tagsList 创建失败')
                return False

            for idx in range(len(目标列表)):
                目标 = 目标列表[idx]
                方式 = 方式列表[idx]
                if isfile(目标):
                    if 方式 == 'copy':
                        shutil.copy2(目标, tgtFolder_public)
                    else:
                        shutil.move(目标, tgtFolder_public)
                if isdir(目标):
                    if 方式 == 'copy':
                        shutil.copytree(目标, os.path.join(tgtFolder_public, 目标))
                    else:
                        shutil.move(目标, os.path.join(tgtFolder_public, 目标))

            画板.消息(f'publishing done: {黄字(tgtFolder_public)} {绿字("✔")}')

            # 如果有需要,可以将发布事件记录到数据库中,方便对齐
            thisV.uploadGitVer(eventName='publish', eventComment='publishSomething')
    except Exception as e:
        画板.提示错误('遇到异常:',e)
        return False


def 打印版本信息(userArgs: 命令行参数类 = None,
                 画板: 打印模板 = None):
    画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
    userArgs = userArgs if isinstance(userArgs, 命令行参数类) else 命令行参数类()
    画板.执行位置(打印版本信息)

    if not userArgs.outputType_0PublishObj_1PrintGitVer == 1:
        画板.提示错误('outputType is noMatched:', userArgs.outputType_0PublishObj_1PrintGitVer)

    thisV: gitVerInfo.GitVerInfo = gitVerInfo.GitVerInfo(userArgs.gitVerInfoCfg)

    if thisV.versionDecode(画板=画板.副本.缩进()):
        thisV.repoInfo.verInfo.showInfo(userArgs.publishType_0Private_1Public_2Both, copyed=userArgs.copy,
                                        语义化提交日期=True,
                                        画板=画板.副本.缩进())
    else:
        画板.提示错误('版本解析失败')

    画板.消息('uploadToSql:', 红字(str(False)))


def 解析版本号(画板: 打印模板 = None):
    画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
    画板.执行位置(解析版本号)

    class git版本类:
        def __init__(self,
                     私有版本号: str = None,
                     公开版本号: str = None,
                     远程仓库: list[gitVerInfo.Remote] = None):
            self.私有版本号: str = 私有版本号
            self.公开版本号: str = 公开版本号
            self.远程仓库: list[gitVerInfo.Remote] = 远程仓库

        def 展示(self, 画板: 打印模板 = None):
            画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
            画板.执行位置(self.__class__, self.展示)

            画板.准备表格()
            画板.添加一行('项目', '值').修饰行(青字)
            画板.添加一行('私有版本号', self.私有版本号)
            画板.添加一行('公开版本号', self.公开版本号)
            画板.添加一行('远程仓库',
                          '\n'.join([f'{仓库.name}: {仓库.url}' for 仓库 in self.远程仓库]) if self.远程仓库 else None)
            画板.展示表格()

    版本: git版本类 = git版本类()

    参数: 命令行参数类 = 命令行参数类()
    # 读取json中的配置
    参数.读取Json配置(画板=画板.副本.缩进())

    参数.outputType_0PublishObj_1PrintGitVer = 1
    参数.publishType_0Private_1Public_2Both = 2

    thisV: gitVerInfo.GitVerInfo = gitVerInfo.GitVerInfo(参数.gitVerInfoCfg)

    if thisV.versionDecode(画板=画板.副本.缩进()):
        版本.私有版本号 = thisV.repoInfo.verInfo.privateVersion
        版本.公开版本号 = thisV.repoInfo.verInfo.publicVersion
        版本.远程仓库 = thisV.repoInfo.remotes
    else:
        画板.提示错误('版本解析失败')

    return 版本


def 打印日志(入参: 命令行参数类 = None,
             所有分支: bool = False,
             日志数量: int = -1,
             语义化提交日期: bool = False,
             画板: 打印模板 = None):
    画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
    画板.执行位置(打印日志)

    if not isinstance(入参, 命令行参数类):
        入参 = 命令行参数类()
        # 读取json中的配置
        入参.读取Json配置(画板=画板.副本.缩进())
        入参.logsCount = 日志数量

    gitVerInfo.GitVerInfo(入参.gitVerInfoCfg).打印日志(日志数量=入参.logsCount,
                                                       所有分支=True if 入参.AllBranches or 所有分支 else False,
                                                       语义化提交日期 =语义化提交日期,
                                                       画板=画板.副本.缩进())

def 打印Tags(入参: 命令行参数类 = None,
             语义化提交日期: bool = False,
             画板: 打印模板 = None):
    画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
    画板.执行位置(打印Tags)

    if not isinstance(入参, 命令行参数类):
        入参 = 命令行参数类()
        # 读取json中的配置
        入参.读取Json配置(画板=画板.副本.缩进())

    gitVerInfo.GitVerInfo(入参.gitVerInfoCfg).打印Tags(画板=画板.副本.缩进())

if __name__ == '__main__':
    画板: 打印模板 = 打印模板(False)
    画板.执行位置(__file__)

    画板.特殊字符宽度字典 = {'ī':2.5}

    # 解析命令行参数
    入参 = 命令行参数类()
    入参.解析入参(画板=画板.副本.缩进())

    # 准备交互接口
    交互接口: 交互接口类 = 交互接口类()
    搜索接口: 搜索接口类 = 搜索接口类(everything服务端口=59864)

    if 入参.gitVerInfoCfg.focusDoc_fileName in ['-c', '--copy']:
        入参.gitVerInfoCfg.focusDoc_fileName = ''
        入参.copy = True

    # 检查匿名参数中是否存在 '-15' 样式的参数,如果存在,将其识别为 logsCount 参数值
    if 入参.匿名参数:
        for 参数 in 入参.匿名参数:
            参数值 = str(参数 if 参数 else '').strip()
            if 参数值 and 参数值[0] == '-' and 参数值[1:].isdigit():
                入参.logsCount = int(参数值[1:])
                break

    if 画板.正在调试:
        入参.展示(画板=画板)

    if 入参.focusDoc_fileName:
        搜索结果: 搜索结果类 = 搜索接口.搜索(搜索关键字=入参.focusDoc_fileName,
                                             参考路径=os.path.dirname(__file__),
                                             画板=画板.副本.缩进())
        if 搜索结果.总数 < 1 and 搜索结果.错误消息:
            画板.消息(f'兴趣文档搜索失败: {搜索结果.错误消息}')
            exit(0)
        elif 搜索结果.总数 == 1:
            if os.path.isfile(搜索结果.结果列表[0]):
                入参.focusDoc_fileName = 搜索结果.结果列表[0]
        elif 搜索结果.总数 > 1:
            画板.消息('存在多个符合条件的文档')
            for itm in 搜索结果.结果列表:
                画板.消息(itm[len(os.path.dirname(__file__)):])
            exit(0)

    if 入参.showLogs:
        打印日志(入参=入参, 语义化提交日期=True, 画板=画板.副本.缩进())
    elif 入参.showTags:
        打印Tags(入参=入参, 语义化提交日期=True, 画板=画板.副本.缩进())
    elif 入参.outputType_0PublishObj_1PrintGitVer == 0:
        发布产品(userArgs=入参, 画板=画板.副本.缩进())
    elif 入参.outputType_0PublishObj_1PrintGitVer == 1:
        打印版本信息(userArgs=入参, 画板=画板.副本.缩进())
    else:
        画板.提示错误('outputType is: ', 入参.outputType_0PublishObj_1PrintGitVer)
