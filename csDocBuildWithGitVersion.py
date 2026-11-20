# -*- coding: utf-8 -*-

# ⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊
# 以下过程将指导你在 visual studio 的 C# 工程/项目中完成必要的配置，以使 visual studio 可以在每次编译/生成时，调用本 py 脚本更新 git 版本信息
# 您需要在 visual studio 的 C# 工程/项目中，添加 getGitVer.cs 文件（添加一次即可）
# 您需要在您使用/调用 git 版本信息的 cs 文件中，引入对 getGitVer 内容的可见性，如下：
# using gitVer; //←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

# 您可以通过 gitVer.cs 中提供的 getGitVer 类中的静态方法获取和使用 git 版本信息，如下：
# gitVer.gitVer.gitVerPrivate  //←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
# gitVer.gitVer.gitVerPublic   //←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

# 为了使 visual sudio 在每次编译/生成 C# 项目时，调用本脚本更新 git 版本信息，您需要在 项目-属性-生成事件-生成前事件命令行 中进行以下配置
# cd $(SolutionDir)
# python csDocBuildWithGitVersion.py
# 注意：在上面的 python 命令行中，请在您的 cmd 环境下测试 python 命令的使用方式，有可能您的电脑上对应的命令是 python3，请适配合适的命令

# region 导入依赖包
import argparse
import os
import sys
import hashlib

# ⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊⛊
# 本脚本依赖于 getGitVer.py 脚本提供的函数功能来获取 git 仓库的版本信息，所以您需要在此指定 getGitVer.py 的位置
sys.path.append(os.path.expanduser('~') + "\\gitVersion")  # ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

try:
    import gitVerInfo
except ImportError as impErr:
    gitVerInfo = None
    print("尝试导入 gitVerInfo 依赖时检测到异常：", impErr)
    exit(0)

try:
    from DebugInfo.DebugInfo import *
except ImportError as impErr:
    print("尝试导入 DebugInfo 依赖时检测到异常：", impErr)
    try:
        os.system("pip install DebugInfo")
    except OSError as osErr:
        print("尝试安装模块 DebugInfo 时检测到异常：", osErr)
        exit(0)
    else:
        try:
            # 如果模块安装成功，则再次尝试导入依赖
            from DebugInfo.DebugInfo import *
        except Exception as expErr:
            print("再次尝试导入 DebugInfo 依赖时检测到异常：", expErr)
            exit(0)
# endregion


# 定义一个 CommandArgs 类，用于记录和传递命令行参数
class CommandArgs:
    ARGS = None
    publishType_0Private_1Public_2Both: int = None
    outputType_0PublishObj_1PrintGitVer: int = 0  # 0: publishObj, 1: printGitVer

    # 定义一gitVerInfoCfg 对象，用于保存对应的配置信息
    gitVerInfoCfg: gitVerInfo.GitVerInfoCfg = None

    tgtCsDocFullName: str = None
    tgtHDocFullName: str = None
    tgtCDocFullName: str = None

    def __init__(self):
        self.gitVerInfoCfg = gitVerInfo.GitVerInfoCfg()

    def copyFrom(self, src=None):
        if isinstance(self, type(src)):
            self.publishType_0Private_1Public_2Both = src.publishType_0Private_1Public_2Both
            self.outputType_0PublishObj_1PrintGitVer = src.outputType_0PublishObj_1PrintGitVer

            self.gitVerInfoCfg = src.gitVerInfoCfg.副本

            self.tgtCsDocFullName = src.tgtCsDocFullName
            self.tgtHDocFullName = src.tgtHDocFullName
            self.tgtCDocFullName = src.tgtCDocFullName

    def showInfo(self, 白板: 调试模板 = 调试模板()):
        白板.执行位置(self.__class__.__name__ + '.showInfo')

        白板.准备表格()
        白板.添加一行('publishType_0Private_1Public_2Both:', self.publishType_0Private_1Public_2Both)
        白板.添加一行('outputType_0PublishObj_1PrintGitVer:', self.outputType_0PublishObj_1PrintGitVer)

        白板.添加一行('tgtCsDocFullName:', self.tgtCsDocFullName)
        白板.添加一行('tgtHDocFullName:', self.tgtHDocFullName)
        白板.添加一行('tgtCDocFullName:', self.tgtCDocFullName)

        白板.添加一行('productId:', self.gitVerInfoCfg.productId)
        白板.添加一行('gitRePoDir:', self.gitVerInfoCfg.gitRePoDir)
        白板.添加一行('majorBranchName:', self.gitVerInfoCfg.majorBranchName)
        白板.添加一行('tagPrefix_major:', self.gitVerInfoCfg.tagPrefix_major)
        白板.添加一行('minorBranchName:', self.gitVerInfoCfg.minorBranchName)
        白板.添加一行('tagPrefix_minor:', self.gitVerInfoCfg.tagPrefix_minor)

        # 在 visual studio 的输出窗口中，无法对对GBK编码进行正确显示，为了避免出错，非GBK编码不进行展示
        # 白板.消息('anchorChar:\t', self.gitVerInfoCfg.anchorChar)

        白板.添加一行('gitVerSql_host:', self.gitVerInfoCfg.mySqlCfg.host)
        白板.添加一行('gitVerSql_user:', self.gitVerInfoCfg.mySqlCfg.user)
        白板.添加一行('gitVerSql_pwd:', self.gitVerInfoCfg.mySqlCfg.pwd)
        白板.添加一行('gitVerSql_db:', self.gitVerInfoCfg.mySqlCfg.db)
        白板.添加一行('gitVerSql_charset:', self.gitVerInfoCfg.mySqlCfg.charset)
        白板.添加一行('gitVerSql_table:', self.gitVerInfoCfg.mySqlCfg.table)

        if 白板.调试状态:
            白板.添加一行('debug model:', 红字(白板.调试状态))
        else:
            白板.添加一行('debug model:', 绿字(白板.调试状态))

        白板.展示表格()

    # 定义一个函数，用来解析命令行调用传入的参数
    def argParseCatch(self, 白板: 调试模板 = 调试模板()) -> bool:
        白板.执行位置(self.__class__.__name__ + '.argParseCatch')

        # 基于 argparse 模块解析脚本调用传入的参数
        parser = argparse.ArgumentParser(description='通过 -h 参数可查阅各参数及其涵义')

        parser.add_argument('--publishType_0Private_1Public_2Both', type=int, help="指定发版的类型")
        parser.add_argument('--outputType_0PublishObj_1PrintGitVer', type=int, help="指定输出类型")
        parser.add_argument('--productID', type=str, help="指定产品ID")

        parser.add_argument('--gitRePoDir', type=str, help="用于解析 git 版本信息的 git 仓库路径")
        parser.add_argument('--majorBranchName', type=str, help="用于追踪major版本的分支名称")
        parser.add_argument('--tagPrefix_major', type=str, help="major分支上被追踪版本信息的tag的前缀")
        parser.add_argument('--minorBranchName', type=str, help="用于追踪minor版本的分支名称")
        parser.add_argument('--tagPrefix_minor', type=str, help="minor分支上被追踪版本信息的tag的前缀")
        parser.add_argument('--anchorChar', type=str, help="打印版本记录时，用于标记版本节点的符号")

        parser.add_argument('--tgtCsDocFullName', type=str, help="指定生成 cs 文件的全路径，包括路径和文件名以及后缀")
        parser.add_argument('--tgtHDocFullName', type=str, help="指定生成 h 文件的全路径，包括路径和文件名以及后缀")
        parser.add_argument('--tgtCDocFullName', type=str, help="指定生成 c 文件的全路径，包括路径和文件名以及后缀")

        parser.add_argument('--gitVerSql_host', type=str, help="用于存储管理 gitVer 信息的数据库 host 信息")
        parser.add_argument('--gitVerSql_user', type=str, help="用于存储管理 gitVer 信息的数据库 user 信息")
        parser.add_argument('--gitVerSql_pwd', type=str, help="用于存储管理 gitVer 信息的数据库 password 信息")
        parser.add_argument('--gitVerSql_db', type=str, help="用于存储管理 gitVer 信息的数据库 database 信息")
        parser.add_argument('--gitVerSql_charset', type=str, help="用于存储管理 gitVer 信息的数据库 charset 信息")
        parser.add_argument('--gitVerSql_table', type=str, help="用于存储管理 gitVer 信息的数据库 tableName 信息")

        self.ARGS = parser.parse_args()

        if self.ARGS.publishType_0Private_1Public_2Both is not None:
            self.publishType_0Private_1Public_2Both = self.ARGS.publishType_0Private_1Public_2Both
        if self.ARGS.outputType_0PublishObj_1PrintGitVer is not None:
            self.outputType_0PublishObj_1PrintGitVer = self.ARGS.outputType_0PublishObj_1PrintGitVer
        if self.ARGS.productID is not None:
            self.gitVerInfoCfg.productId = self.ARGS.productID
        if self.ARGS.gitRePoDir:
            self.gitVerInfoCfg.gitRePoDir = self.ARGS.gitRePoDir
        if self.ARGS.majorBranchName:
            self.gitVerInfoCfg.majorBranchName = self.ARGS.majorBranchName
        if self.ARGS.minorBranchName:
            self.gitVerInfoCfg.minorBranchName = self.ARGS.minorBranchName
        if self.ARGS.tagPrefix_major:
            self.gitVerInfoCfg.tagPrefix_major = self.ARGS.tagPrefix_major
        if self.ARGS.tagPrefix_minor:
            self.gitVerInfoCfg.tagPrefix_minor = self.ARGS.tagPrefix_minor
        if self.ARGS.tgtCsDocFullName:
            self.gitVerInfoCfg.tgtCsDocFullName = self.ARGS.tgtCsDocFullName
        if self.ARGS.tgtHDocFullName:
            self.gitVerInfoCfg.tgtHDocFullName = self.ARGS.tgtHDocFullName
        if self.ARGS.tgtCDocFullName:
            self.gitVerInfoCfg.tgtCDocFullName = self.ARGS.tgtCDocFullName
        if self.ARGS.anchorChar:
            self.gitVerInfoCfg.anchorChar = self.ARGS.anchorChar

        if self.ARGS.gitVerSql_host:
            self.gitVerInfoCfg.gitVerSql_host = self.ARGS.gitVerSql_host
        if self.ARGS.gitVerSql_user:
            self.gitVerInfoCfg.gitVerSql_user = self.ARGS.gitVerSql_user
        if self.ARGS.gitVerSql_pwd:
            self.gitVerInfoCfg.gitVerSql_pwd = self.ARGS.gitVerSql_pwd
        if self.ARGS.gitVerSql_db:
            self.gitVerInfoCfg.gitVerSql_db = self.ARGS.gitVerSql_db
        if self.ARGS.gitVerSql_charset:
            self.gitVerInfoCfg.gitVerSql_charset = self.ARGS.gitVerSql_charset
        if self.ARGS.gitVerSql_table:
            self.gitVerInfoCfg.gitVerSql_table = self.ARGS.gitVerSql_table

        return True


# 定义输入参数变量，用来存储和管理用户的输入参数
defaultArgs = CommandArgs()

# region 设置输入变量的默认参数
# 脚本需要知道您希望在哪个 git 仓库中获取版本信息，请在此配置您的 git 仓库路径，默认本脚本被调用工作的路径下的 git 仓库
defaultArgs.gitVerInfoCfg.gitRePoDir = os.getcwd()
# getGitVer 中的函数需要您指定 git 仓库的 major 版本分支和 minor 版本分支，请在此配置您的 major 分支名
defaultArgs.gitVerInfoCfg.majorBranchName = 'master'

# getGitVer 中的函数需要您指定 git 仓库的 major 版本分支和 minor 版本分支，请在此配置您的 minor 分支名
defaultArgs.gitVerInfoCfg.minorBranchName = 'release'

# getGitVer 中的函数需要您指定用于表示版本信息的 tag 的前缀，请在此配置你用在 major 分支上的有发版意义的 tag 前缀，例如 m1,m2,m3等
defaultArgs.gitVerInfoCfg.tagPrefix_major = 'm'

# getGitVer 中的函数需要您指定用于表示版本信息的 tag 的前缀，请在此配置你用在 minor 分支上的有发版意义的 tag 前缀，例如 r1,r2,r3等
defaultArgs.gitVerInfoCfg.tagPrefix_minor = 'r'

# 在打印版本记录时，用于标记版本节点位置的符号，默认符号为 ⚓
defaultArgs.gitVerInfoCfg.anchorChar = '⚓'


# 用于存储管理 gitVer 信息的数据库 host 信息
defaultArgs.gitVerInfoCfg.gitVerSql_host = '127.0.0.1'

# 用于存储管理 gitVer 信息的数据库 user 信息
defaultArgs.gitVerInfoCfg.gitVerSql_user = 'userName'

# 用于存储管理 gitVer 信息的数据库 password 信息
defaultArgs.gitVerInfoCfg.gitVerSql_pwd = '***'

# 用于存储管理 gitVer 信息的数据库 database 信息
defaultArgs.gitVerInfoCfg.gitVerSql_db = 'dbName'

# 用于存储管理 gitVer 信息的数据库 charset 信息
defaultArgs.gitVerInfoCfg.gitVerSql_charset = 'utf8'

# 用于存储管理 gitVer 信息的数据库 tableName 信息
defaultArgs.gitVerInfoCfg.gitVerSql_table = 'tableName'

defaultArgs.tgtCsDocFullName = 'gitVer.cs'  # 默认的需要导出生成的 cs 文档名称
defaultArgs.tgtHDocFullName = 'gitVer.h'  # 默认的需要导出生成的 h 文档名称
defaultArgs.tgtCDocFullName = 'gitVer.c'  # 默认的需要导出生成的 c 文档名称
defaultArgs.objToBePublished = None  # 默认需要进行 publish 的对象为 None
defaultArgs.publishType_0Private_1Public_2Both = 2  # 默认 publishType 为 1：for public
defaultArgs.outputType_0PublishObj_1PrintGitVer = 0  # 默认 outputType 为 0： for publishObj
# endregion 默认参数设置完毕


def csDocBuildWithGitVersion(userArgs: CommandArgs = None, 画板: 打印模板 = None) -> bool:
    global defaultArgs
    画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
    if not userArgs:
        userArgs = CommandArgs()
        userArgs.copyFrom(defaultArgs)

    画板.执行位置(csDocBuildWithGitVersion)

    if not userArgs.outputType_0PublishObj_1PrintGitVer == 0:
        画板.提示错误('outputType is noMatched:', userArgs.outputType_0PublishObj_1PrintGitVer)

    thisV: gitVerInfo.GitVerInfo = gitVerInfo.GitVerInfo(userArgs.gitVerInfoCfg)

    flg = thisV.versionDecode()
    if not flg:
        画板.提示错误('版本解析失败')
        return False

    画板.消息('gitV public:', thisV.repoInfo.verInfo.publicVersion)
    画板.消息('gitV private:', thisV.repoInfo.verInfo.privateVersion)

    # 保存 tagsList 信息，与 tgtCsDocFullName 同路径
    saveFlg, tgtDoc = thisV.repoInfo.verInfo.saveTagsList(objPublished=os.path.abspath(userArgs.tgtCsDocFullName),
                                                          saveType_0Private_1Public_2Both=2,
                                                          画板=画板.副本.缩进())
    if not saveFlg:
        画板.提示错误('tagsList save failed')
    else:
        画板.消息('tagsList saved: ', tgtDoc)

    if saveFlg:
        # 计算 tagsList 文档的 md5 指纹
        md5Obj = hashlib.md5()
        if os.path.isfile(tgtDoc):
            with open(tgtDoc, 'rb') as fObj:
                while True:
                    data = fObj.read(4096)
                    if not data:
                        break
                    md5Obj.update(data)
        mHash: str = md5Obj.hexdigest()

        # 整理将要写入 gitVersion.cs 文档中的内容
        ARGS_Str_ = str(userArgs.ARGS)
        fstr = '//tgtCsDocFullName is: ' + userArgs.tgtCsDocFullName + '\n'
        if ARGS_Str_ != '':
            fstr = fstr + '//ARGS is: ' + ARGS_Str_ + '\n'
        fstr = fstr + '//git Repo is: ' + userArgs.gitVerInfoCfg.gitRePoDir + '\n'
        fstr = fstr + '\nnamespace gitVerInfo' + \
                      '\n{' + \
                      '\n\tclass gitVer' + \
                      '\n\t{' + \
                      '\n\t\tstatic public readonly string productID = "' + thisV.repoInfo.gitVerInfoCfg.productId + '";' + \
                      '\n\t\tstatic public readonly string md5_tagListDoc = "' + mHash + '";' + \
                      '\n\t\tstatic public readonly string gitVerPublic = "' + thisV.repoInfo.verInfo.publicVersion + '";' + \
                      '\n\t\tstatic public readonly string gitVerPrivate = "' + thisV.repoInfo.verInfo.privateVersion + '";' + \
                      '\n\t\tstatic public readonly string sqlHost = "' + thisV.mysqlInfo.mySqlCfg.host + '";' + \
                      '\n\t\tstatic public readonly string sqlUser = "' + thisV.mysqlInfo.mySqlCfg.user + '";' + \
                      '\n\t\tstatic public readonly string sqlPwd = "' + thisV.mysqlInfo.mySqlCfg.pwd + '";' + \
                      '\n\t\tstatic public readonly string sqlDb = "' + thisV.mysqlInfo.mySqlCfg.db + '";' + \
                      '\n\t\tstatic public readonly string sqlCharset = "' + thisV.mysqlInfo.mySqlCfg.charset + '";' + \
                      '\n\t\tstatic public readonly string sqlTable = "' + thisV.mysqlInfo.mySqlCfg.table + '";' + \
                      '\n\t}' + \
                      '\n}'
        # 打印 fstr 字符串值，以便调试排查问题
        画板.调试消息(fstr)

        # 尝试打开 tgtCsDocFullName 文档，并向其写入内容
        csDocEnable = False
        csDoc = None
        try:
            # 尝试以写模式打开 cs 文档，当 cs 文档不存在时，创建一个
            tgtCsDocFullNameExistFlg = os.path.isfile(userArgs.tgtCsDocFullName)
            csDoc = open(userArgs.tgtCsDocFullName, 'w', encoding='utf-8')
            csDocEnable = True
        except Exception as e:
            画板.提示错误('创建文档', userArgs.tgtCsDocFullName, '出现异常：', e)
        else:
            if csDocEnable:
                if tgtCsDocFullNameExistFlg:
                    画板.调试消息('打开 cs 文档成功：', userArgs.tgtCsDocFullName)
                else:
                    画板.调试消息('创建 cs 文档成功：', userArgs.tgtCsDocFullName)
            else:
                画板.调试消息('cs 文档不可用：', userArgs.tgtCsDocFullName)

        if fstr and csDocEnable:
            try:
                csDoc.write(fstr)
            except Exception as e:
                画板.提示错误('向 cs 文档写入gitVersion信息时出错:', e)
            else:
                画板.消息('向 cs 文档写入 gitVersion 信息完成:', os.path.abspath(userArgs.tgtCsDocFullName))
            finally:
                if csDoc:
                    csDoc.close()
                    画板.消息('关闭 cs 文档成功')

        # 整理gitCommit信息
        gitCommit: str = "unknown"
        if thisV.repoInfo.currBranchCommitsList:
            gitCommit = thisV.repoInfo.currBranchCommitsList[0].commit.strip()[:7]
        dirtyFlg = 1 if thisV.repoInfo.verInfo.dirtyTimeStamp else 0

        #region 整理将要写入 gitVersion.h 文档中的内容
        fstrh: str = (f'#ifndef GIT_VERSION_INFO_\n#define GIT_VERSION_INFO_\n'
                      f'#define GIT_COMMIT "{gitCommit}"\n'
                      f'#define GIT_DIRTY_FLG {dirtyFlg}\n\n'
                      f'#include <stdint.h>\n\n'
                      f'typedef struct{{\n\tuint8_t dirtyFlg;\n\tuint8_t gitCommit[];\n}}gitVerInfo_t;\n\n'
                      f'extern const gitVerInfo_t gitVerInfo;\n\n'
                      f'#endif\n')

        # 打印 fstrh 字符串值，以便调试排查问题
        画板.调试消息(fstrh)

        # 尝试打开 tgtHDocFullName 文档，并向其写入内容
        csDocEnable = False
        csDoc = None
        try:
            # 尝试以写模式打开 cs 文档，当 cs 文档不存在时，创建一个
            tgtHDocFullNameExistFlg = os.path.isfile(userArgs.tgtHDocFullName)
            csDoc = open(userArgs.tgtHDocFullName, 'w', encoding='utf-8')
            csDocEnable = True
        except Exception as e:
            画板.提示错误('创建文档', userArgs.tgtHDocFullName, '出现异常：', e)
        else:
            if csDocEnable:
                if tgtHDocFullNameExistFlg:
                    画板.调试消息('打开 h 文档成功：', userArgs.tgtHDocFullName)
                else:
                    画板.调试消息('创建 h 文档成功：', userArgs.tgtHDocFullName)
            else:
                画板.调试消息('h 文档不可用：', userArgs.tgtHDocFullName)

        if fstrh and csDocEnable:
            try:
                csDoc.write(fstrh)
            except Exception as e:
                画板.提示错误('向 h 文档写入gitVersion信息时出错:', e)
            else:
                画板.消息('向 h 文档写入 gitVersion 信息完成:', os.path.abspath(userArgs.tgtHDocFullName))
            finally:
                if csDoc:
                    csDoc.close()
                    画板.消息('关闭 h 文档成功')
        #endregion

        # region 整理将要写入 gitVersion.c 文档中的内容
        fstrh: str = (f'#include "{userArgs.tgtHDocFullName}"\n\n'
                      f'const gitVerInfo_t gitVerInfo = {{\n\t.gitCommit = "{gitCommit}",\n\t.dirtyFlg = {dirtyFlg}\n}};\n\n')

        # 打印 fstrh 字符串值，以便调试排查问题
        画板.调试消息(fstrh)

        # 尝试打开 tgtHDocFullName 文档，并向其写入内容
        csDocEnable = False
        csDoc = None
        try:
            # 尝试以写模式打开 cs 文档，当 cs 文档不存在时，创建一个
            tgtHDocFullNameExistFlg = os.path.isfile(userArgs.tgtCDocFullName)
            csDoc = open(userArgs.tgtCDocFullName, 'w', encoding='utf-8')
            csDocEnable = True
        except Exception as e:
            画板.提示错误('创建文档', userArgs.tgtCDocFullName, '出现异常：', e)
        else:
            if csDocEnable:
                if tgtHDocFullNameExistFlg:
                    画板.调试消息('打开 h 文档成功：', userArgs.tgtCDocFullName)
                else:
                    画板.调试消息('创建 h 文档成功：', userArgs.tgtCDocFullName)
            else:
                画板.调试消息('c 文档不可用：', userArgs.tgtCDocFullName)

        if fstrh and csDocEnable:
            try:
                csDoc.write(fstrh)
            except Exception as e:
                画板.提示错误('向 c 文档写入gitVersion信息时出错:', e)
            else:
                画板.消息('向 c 文档写入 gitVersion 信息完成:', os.path.abspath(userArgs.tgtCDocFullName))
            finally:
                if csDoc:
                    csDoc.close()
                    画板.消息('关闭 c 文档成功')
        # endregion



if __name__ == '__main__':
    画板 = 打印模板()
    画板.执行位置(__file__)

    thisARGS = CommandArgs()
    # 加载默认配置参数
    thisARGS.copyFrom(defaultArgs)
    # 如果存在配置文件，则需要读取配置文件
    if os.path.exists('gitVerInfoCfg.json'):
        thisARGS.gitVerInfoCfg.readJson(gitVerInfoCfgDir=os.path.abspath('gitVerInfoCfg.json'),
                                        白板=画板.副本.缩进())

    # 解析脚本调用传入的参数
    thisARGS.argParseCatch()
    thisARGS.showInfo()

    csDocBuildWithGitVersion(userArgs=thisARGS, 画板=画板)
